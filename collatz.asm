; ============================================================
; collatz.asm - Demonstration de la conjecture de Collatz (3n + 1)
; Utilise : MOV, ADD, MUL, DIV, MOD, MSG, JMP, BEQ, BNE, BGT
; ============================================================

; --- Initialisation ---
MOV R0, 3000        ; R0 = nombre de depart (N)
MOV R1, 0        ; R1 = compteur d'etapes = 0
MSG "Debut de la conjecture de Collatz pour N = R0"

loop:
    ADD R1, R1, 1    ; incrementer le compteur d'etapes

    ; Verification de la parite : R2 = R0 % 2
    MOD R2, R0, 2
    MOV R3, 0
    BEQ R2, R3, even_branch

    ; --- Cas Impair (3 * N + 1) ---
    MUL R0, R0, 3
    ADD R0, R0, 1
    JMP next_step

even_branch:
    ; --- Cas Pair (N / 2) ---
    DIV R0, R0, 2

next_step:
    MSG "Etape R1 : N = R0"

    ; Si R0 == 1 -> fin du programme
    MOV R4, 1
    BEQ R0, R4, done

    ; Sinon, continuer la boucle
    JMP loop

done:
    MSG "Conjecture de Collatz terminee en R1 etapes !"
