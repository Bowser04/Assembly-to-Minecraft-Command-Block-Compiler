; basic_sample.asm
; Exemple d'un programme assembleur utilisant uniquement les instructions actuellement gérées:
; MOV, ADD, SUB, MUL, DIV, MOD, JMP, BEQ, BNE, BGT, BLT
; (Sans instructions RAM LDR/STR)

; --- Initialisation des registres ---
MOV R0, 0        ; R0 = sum = 0
MOV R1, 1        ; R1 = i = 1
MOV R2, 10       ; R2 = N = 10

; --- Boucle principal: calcul de la somme 1..10 ---
loop_sum:
ADD R0, R0, R1   ; R0 = R0 + R1 (sum += i)
ADD R1, R1, 1    ; R1 = R1 + 1  (i++)
BGT R1, R2, end_sum  ; if i > N, jump to end_sum
JMP loop_sum

end_sum:
    MSG "Somme de 1 a 10 calculee. Somme = R0"
    ; --- Opérations arithmétiques complémentaires ---
MOV R3, 7
MUL R4, R0, R3   ; R4 = sum * 7
DIV R5, R4, 4    ; R5 = R4 / 4 (quotient)
MOD R6, R4, 4    ; R6 = R4 % 4 (reste)

MOV R7, 0
BEQ R6, R7, divisible

; Pas divisible par 4
MOV R7, 99
JMP done

divisible:
MOV R7, 1

done:
    MSG "Programme termine. Divisibilite par 4 de R4 : R7 (1=Divisible, 99=Non divisible)"
    ; Fin du programme
