import tkinter as tk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from emulator import Emulator

class Debugger(Emulator):
    def __init__(self, reg_size, output_callback=None, minecraft_tick=False):
        super().__init__(reg_size, minecraft_tick=minecraft_tick)
        self.script_lines = []
        self.paused = True
        self.last_error = None
        self.output_callback = output_callback

    def load_script(self, script):
        self.script_lines = script.splitlines()
        self.find_labels(self.script_lines)
        self.script = self.script_lines
        self.line = 0
        self.end = False
        self.last_error = None

    def step(self):
        if self.end or self.line >= len(self.script_lines):
            self.end = True
            return False
        try:
            self.execute_line(self.script_lines[self.line])
            self.last_error = None
        except Exception as e:
            self.last_error = str(e)
            self.end = True
        return True

    def handle_say(self, line, *kwargs):
        # Override to capture output
        text = super().handle_say(line, return_text=True)
        if self.output_callback:
            self.output_callback(text)

    def get_state(self): 
        return {
            'line': self.line,
            'current': self.script_lines[self.line] if self.line < len(self.script_lines) else '',
            'registers': dict(self.REGISTERS),
            'variables': dict(self.VARIABLE),
            'stack': list(self.STACK),
            'last_error': self.last_error
        }

class DebuggerUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Assembly Debugger')
        self.root.geometry('1200x700')
        self.debugger = None
        self.script_loaded = False
        self.running = False
        self.speed = 0  # 0=max, 1=minecraft tick (50ms), 2=custom
        self.custom_speed = 100  # milliseconds
        self.create_widgets()

    def create_widgets(self):
        # Main container with padding
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top bar with controls and status
        top_bar = tk.Frame(main_frame, bg='#f0f0f0')
        top_bar.pack(fill=tk.X, pady=(0, 10))

        # Controls frame
        controls = tk.LabelFrame(top_bar, text='Controls', font=('Arial', 10, 'bold'), bg='#f0f0f0', padx=10, pady=5)
        controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load button with icon-like style
        self.load_btn = tk.Button(controls, text='📁 Load Script', command=self.load_script, 
                                   bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), 
                                   padx=15, pady=8, relief=tk.RAISED, cursor='hand2')
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # Step button
        self.step_btn = tk.Button(controls, text='▶ Step', command=self.step, state=tk.DISABLED,
                                  bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                                  padx=15, pady=8, relief=tk.RAISED, cursor='hand2')
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        # Run button
        self.run_btn = tk.Button(controls, text='▶▶ Run All', command=self.toggle_run, state=tk.DISABLED,
                                 bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                                 padx=15, pady=8, relief=tk.RAISED, cursor='hand2')
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        self.reset_btn = tk.Button(controls, text='🔄 Reset', command=self.reset, state=tk.DISABLED,
                                   bg='#9E9E9E', fg='white', font=('Arial', 10, 'bold'),
                                   padx=15, pady=8, relief=tk.RAISED, cursor='hand2')
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Separator
        sep = tk.Frame(controls, width=2, bg='#bdc3c7')
        sep.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Speed control
        speed_label = tk.Label(controls, text='Speed:', font=('Arial', 10, 'bold'), 
                              bg='#f0f0f0', fg='#2c3e50')
        speed_label.pack(side=tk.LEFT, padx=(5, 10))
        
        self.speed_var = tk.IntVar(value=0)
        speed_max = tk.Radiobutton(controls, text='Max', variable=self.speed_var, value=0,
                                   bg='#f0f0f0', font=('Arial', 9), cursor='hand2',
                                   command=self.update_speed)
        speed_max.pack(side=tk.LEFT, padx=2)
        
        speed_mc = tk.Radiobutton(controls, text='MC Tick (50ms)', variable=self.speed_var, value=1,
                                  bg='#f0f0f0', font=('Arial', 9), cursor='hand2',
                                  command=self.update_speed)
        speed_mc.pack(side=tk.LEFT, padx=2)
        
        speed_custom = tk.Radiobutton(controls, text='Custom:', variable=self.speed_var, value=2,
                                      bg='#f0f0f0', font=('Arial', 9), cursor='hand2',
                                      command=self.update_speed)
        speed_custom.pack(side=tk.LEFT, padx=2)
        
        self.custom_speed_entry = tk.Entry(controls, width=5, font=('Arial', 9))
        self.custom_speed_entry.insert(0, '100')
        self.custom_speed_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(controls, text='ms', font=('Arial', 9), bg='#f0f0f0').pack(side=tk.LEFT)

        # Status label
        self.status_label = tk.Label(controls, text='No script loaded', font=('Arial', 10), 
                                     bg='#f0f0f0', fg='#666')
        self.status_label.pack(side=tk.LEFT, padx=20)

        # Content area
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Script view
        left_panel = tk.Frame(content_frame, bg='#f0f0f0')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        script_header = tk.Label(left_panel, text='Assembly Code', font=('Arial', 11, 'bold'),
                                bg='#2c3e50', fg='white', pady=5)
        script_header.pack(fill=tk.X)

        script_frame = tk.Frame(left_panel, bg='white', relief=tk.SUNKEN, bd=2)
        script_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add line numbers column
        self.line_numbers = tk.Text(script_frame, width=4, bg='#e8e8e8', fg='#666',
                                   state=tk.DISABLED, font=('Consolas', 10), padx=5)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.script_text = tk.Text(script_frame, width=50, state=tk.DISABLED, 
                                  font=('Consolas', 10), bg='white', fg='#2c3e50',
                                  wrap=tk.NONE, padx=5, pady=5)
        self.script_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for script
        script_scroll = tk.Scrollbar(script_frame, command=self.script_text.yview)
        script_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.script_text.config(yscrollcommand=script_scroll.set)

        # Right panel - State view with tabs
        right_panel = tk.Frame(content_frame, bg='#f0f0f0')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        state_header = tk.Label(right_panel, text='Execution State', font=('Arial', 11, 'bold'),
                               bg='#2c3e50', fg='white', pady=5)
        state_header.pack(fill=tk.X)

        from tkinter import ttk
        style = ttk.Style()
        style.configure('Custom.TNotebook', background='#f0f0f0')
        style.configure('Custom.TNotebook.Tab', padding=[20, 10], font=('Arial', 10))
        
        self.notebook = ttk.Notebook(right_panel, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Combined Memory tab (Registers + Variables)
        memory_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(memory_frame, text='💾 Memory')
        
        # Create treeview for registers
        reg_label = tk.Label(memory_frame, text='Registers', font=('Arial', 10, 'bold'),
                            bg='#ecf0f1', fg='#2c3e50', anchor='w', padx=10, pady=5)
        reg_label.pack(fill=tk.X)
        
        self.reg_tree = ttk.Treeview(memory_frame, columns=('Name', 'Value'), show='headings', height=8)
        self.reg_tree.heading('Name', text='Register')
        self.reg_tree.heading('Value', text='Value')
        self.reg_tree.column('Name', width=100, anchor='w')
        self.reg_tree.column('Value', width=150, anchor='e')
        self.reg_tree.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Style for treeview
        style.configure('Treeview', font=('Consolas', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
        # Separator
        sep = tk.Frame(memory_frame, height=2, bg='#bdc3c7')
        sep.pack(fill=tk.X, padx=5, pady=10)
        
        # Create treeview for variables
        var_label = tk.Label(memory_frame, text='Variables', font=('Arial', 10, 'bold'),
                            bg='#ecf0f1', fg='#2c3e50', anchor='w', padx=10, pady=5)
        var_label.pack(fill=tk.X)
        
        self.var_tree = ttk.Treeview(memory_frame, columns=('Name', 'Value'), show='headings', height=6)
        self.var_tree.heading('Name', text='Variable')
        self.var_tree.heading('Value', text='Value')
        self.var_tree.column('Name', width=100, anchor='w')
        self.var_tree.column('Value', width=150, anchor='e')
        self.var_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Stack tab
        stack_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(stack_frame, text='📚 Stack')
        
        stack_label = tk.Label(stack_frame, text='Stack (Top to Bottom)', font=('Arial', 10, 'bold'),
                              bg='#ecf0f1', fg='#2c3e50', anchor='w', padx=10, pady=5)
        stack_label.pack(fill=tk.X)
        
        self.stack_tree = ttk.Treeview(stack_frame, columns=('Index', 'Value'), show='headings')
        self.stack_tree.heading('Index', text='Index')
        self.stack_tree.heading('Value', text='Value')
        self.stack_tree.column('Index', width=100, anchor='center')
        self.stack_tree.column('Value', width=150, anchor='e')
        self.stack_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Error/Output tab
        output_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(output_frame, text='📤 Output')
        
        self.tab_output = scrolledtext.ScrolledText(output_frame, font=('Consolas', 10),
                                                    fg='#2c3e50', bg='#f9f9f9',
                                                    relief=tk.FLAT, padx=10, pady=10, wrap=tk.WORD)
        self.tab_output.pack(fill=tk.BOTH, expand=True)

    def load_script(self):
        file_path = filedialog.askopenfilename(
            title='Select Assembly Script',
            filetypes=[('Assembly Files', '*.asm'), ('All Files', '*.*')]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                script = f.read()
            # Use minecraft tick if speed is set to MC Tick
            use_mc_tick = (self.speed_var.get() == 1)
            self.debugger = Debugger(reg_size=8, output_callback=self.on_output, minecraft_tick=use_mc_tick)
            self.debugger.load_script(script)
            self.script_loaded = True
            self.step_btn.config(state=tk.NORMAL)
            self.run_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            self.display_script()
            self.update_state()
            filename = file_path.split('/')[-1].split('\\')[-1]
            self.status_label.config(text=f'✓ Loaded: {filename}', fg='#27ae60')
            self.root.title(f'Assembly Debugger - {filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load script:\n{str(e)}')
            self.status_label.config(text='✗ Failed to load script', fg='#e74c3c')

    def step(self):
        if not self.script_loaded:
            return
        if not self.debugger.end:
            self.debugger.step()
            self.update_state()
            if self.debugger.end:
                if self.debugger.last_error:
                    self.status_label.config(text='✗ Execution stopped with error', fg='#e74c3c')
                    self.notebook.select(2)  # Switch to output tab
                else:
                    self.status_label.config(text='✓ Execution completed', fg='#27ae60')
    
    def update_speed(self):
        """Update speed settings when radio buttons change"""
        self.speed = self.speed_var.get()
        if self.speed == 2:  # Custom
            try:
                self.custom_speed = max(1, int(self.custom_speed_entry.get()))
            except ValueError:
                self.custom_speed = 100
                self.custom_speed_entry.delete(0, tk.END)
                self.custom_speed_entry.insert(0, '100')
        
        # Update minecraft_tick setting if debugger is loaded
        if self.debugger:
            self.debugger.minecraft_tick = (self.speed == 1)
    
    def toggle_run(self):
        """Toggle between running and paused state"""
        if not self.script_loaded:
            return
        
        if self.running:
            # Stop running
            self.running = False
            self.run_btn.config(text='▶▶ Run All', bg='#FF9800')
            self.step_btn.config(state=tk.NORMAL)
            self.status_label.config(text='⏸ Paused', fg='#f39c12')
        else:
            # Start running
            self.running = True
            self.run_btn.config(text='⏸ Pause', bg='#e74c3c')
            self.step_btn.config(state=tk.DISABLED)
            self.status_label.config(text='▶ Running...', fg='#f39c12')
            self.run_continuous()
    
    def run_continuous(self):
        """Run continuously with real-time updates"""
        if not self.running or self.debugger.end:
            self.running = False
            self.run_btn.config(text='▶▶ Run All', bg='#FF9800')
            self.step_btn.config(state=tk.NORMAL)
            if self.debugger.end:
                if self.debugger.last_error:
                    self.status_label.config(text='✗ Execution stopped with error', fg='#e74c3c')
                    self.notebook.select(2)
                else:
                    self.status_label.config(text='✓ Execution completed', fg='#27ae60')
            return
        
        # Execute one step
        self.debugger.step()
        self.update_state()
        
        # Calculate delay based on speed setting
        delay = 0
        if self.speed == 1:  # Minecraft tick - emulator handles the delays internally
            delay = 0  # No UI delay, emulator time.sleep() handles it
        elif self.speed == 2:  # Custom
            try:
                delay = max(1, int(self.custom_speed_entry.get()))
            except ValueError:
                delay = 100
        
        # Schedule next step
        if delay > 0:
            self.root.after(delay, self.run_continuous)
        else:  # Max speed or MC tick (emulator handles delays)
            self.root.after(1, self.run_continuous)
    
    def run_to_end(self):
        if not self.script_loaded:
            return
        self.status_label.config(text='⚙ Running...', fg='#f39c12')
        self.root.update()
        step_count = 0
        while not self.debugger.end and step_count < 10000:  # Safety limit
            self.debugger.step()
            step_count += 1
            if step_count % 100 == 0:  # Update UI periodically
                self.root.update()
        self.update_state()
        if step_count >= 10000:
            self.status_label.config(text='⚠ Stopped: maximum steps reached', fg='#e67e22')
        elif self.debugger.last_error:
            self.status_label.config(text='✗ Execution stopped with error', fg='#e74c3c')
            self.notebook.select(2)  # Switch to output tab
        else:
            self.status_label.config(text=f'✓ Completed in {step_count} steps', fg='#27ae60')

    def on_output(self, text):
        """Callback for SAY command output"""
        self.tab_output.config(state=tk.NORMAL)
        self.tab_output.insert(tk.END, f'{text}\n', 'output')
        self.tab_output.tag_config('output', foreground='#27ae60', font=('Consolas', 10))
        self.tab_output.see(tk.END)
        self.tab_output.config(state=tk.DISABLED)

    def reset(self):
        if not self.script_loaded:
            return
        # Stop running if currently running
        if self.running:
            self.running = False
            self.run_btn.config(text='▶▶ Run All', bg='#FF9800')
        
        self.debugger.load_script('\n'.join(self.debugger.script_lines))
        self.step_btn.config(state=tk.NORMAL)
        self.run_btn.config(state=tk.NORMAL)
        # Clear output tab
        self.tab_output.config(state=tk.NORMAL)
        self.tab_output.delete('1.0', tk.END)
        self.tab_output.config(state=tk.DISABLED)
        self.update_state()
        self.status_label.config(text='↻ Reset to start', fg='#3498db')

    def update_state(self):
        state = self.debugger.get_state()
        self.highlight_script_line(state['line'])

        # Update Registers table
        for item in self.reg_tree.get_children():
            self.reg_tree.delete(item)
        for k, v in sorted(state['registers'].items()):
            self.reg_tree.insert('', tk.END, values=(k, v))

        # Update Variables table
        for item in self.var_tree.get_children():
            self.var_tree.delete(item)
        if state['variables']:
            for k, v in sorted(state['variables'].items()):
                val_str = str(v) if v is not None else 'None'
                self.var_tree.insert('', tk.END, values=(k, val_str))

        # Update Stack table
        for item in self.stack_tree.get_children():
            self.stack_tree.delete(item)
        if state['stack']:
            for i, v in enumerate(reversed(state['stack'])):
                self.stack_tree.insert('', tk.END, values=(f'[{len(state["stack"])-i-1}]', v))

        # Update Output/Error tab
        self.tab_output.config(state=tk.NORMAL)
        if state['last_error']:
            # Keep previous content and add error
            self.tab_output.insert(tk.END, f'\n[ERROR at Line {state["line"]}]\n', 'error')
            self.tab_output.insert(tk.END, f'{state["last_error"]}\n\n', 'error_detail')
            self.tab_output.tag_config('error', foreground='#e74c3c', font=('Arial', 10, 'bold'))
            self.tab_output.tag_config('error_detail', foreground='#c0392b')
            self.tab_output.see(tk.END)
            self.notebook.select(2)  # Switch to output tab
        self.tab_output.config(state=tk.DISABLED)

        if self.debugger.end:
            self.step_btn.config(state=tk.DISABLED)
            self.run_btn.config(state=tk.DISABLED)

    def display_script(self):
        self.script_text.config(state=tk.NORMAL)
        self.line_numbers.config(state=tk.NORMAL)
        self.script_text.delete('1.0', tk.END)
        self.line_numbers.delete('1.0', tk.END)
        for i, line in enumerate(self.debugger.script_lines):
            self.line_numbers.insert(tk.END, f'{i}\n')
            self.script_text.insert(tk.END, f'{line}\n')
            # Color code different instruction types
            if line.strip().startswith(':'):
                self.script_text.tag_add('label', f'{i+1}.0', f'{i+1}.end')
            elif any(line.strip().startswith(cmd) for cmd in ['ADD', 'SUB', 'MUL', 'DIV']):
                self.script_text.tag_add('arithmetic', f'{i+1}.0', f'{i+1}.end')
            elif any(line.strip().startswith(cmd) for cmd in ['GOTO', 'CALL', 'RET', 'IF']):
                self.script_text.tag_add('control', f'{i+1}.0', f'{i+1}.end')
        
        # Configure syntax highlighting tags
        self.script_text.tag_config('label', foreground='#8e44ad')
        self.script_text.tag_config('arithmetic', foreground='#2980b9')
        self.script_text.tag_config('control', foreground='#e74c3c')
        
        self.script_text.config(state=tk.DISABLED)
        self.line_numbers.config(state=tk.DISABLED)

    def highlight_script_line(self, line_num):
        self.script_text.config(state=tk.NORMAL)
        self.line_numbers.config(state=tk.NORMAL)
        
        # Remove previous highlighting
        self.script_text.tag_remove('highlight', '1.0', tk.END)
        self.line_numbers.tag_remove('highlight_num', '1.0', tk.END)
        
        if 0 <= line_num < len(self.debugger.script_lines):
            # Highlight current line in script
            start = f'{line_num+1}.0'
            end = f'{line_num+1}.end'
            self.script_text.tag_add('highlight', start, end)
            self.script_text.tag_config('highlight', background='#fff176', foreground='#000000')
            
            # Highlight line number
            self.line_numbers.tag_add('highlight_num', f'{line_num+1}.0', f'{line_num+1}.end')
            self.line_numbers.tag_config('highlight_num', background='#ffc107', foreground='#000000', font=('Consolas', 10, 'bold'))
            
            # Auto-scroll to visible
            self.script_text.see(start)
            self.line_numbers.see(start)
        
        self.script_text.config(state=tk.DISABLED)
        self.line_numbers.config(state=tk.DISABLED)

if __name__ == '__main__':
    root = tk.Tk()
    app = DebuggerUI(root)
    root.mainloop()
