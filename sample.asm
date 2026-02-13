; sample.asm
; Exemple d'un petit programme utilisant:
; MOV, LDR, STR, ADD, SUB, MUL, DIV, MOD, JMP, BEQ, BGT, BLT
;
; Butée: mémoire RAM représentée par des offsets (0,1,2,...)
; Registres: R0..R7 (Scoreboards)

; --- Initialisation RAM / constantes ---
MOV R3, 10       ; R3 <- constante N (ici 10)
STR R3, 0        ; RAM[0] <- N

; --- Charger N depuis la RAM ---
LDR R0, 0        ; R0 <- RAM[0]   (N)

; --- Calcul: somme des entiers 1..N ---
MOV R1, 0        ; R1 <- sum = 0
MOV R2, 1        ; R2 <- i = 1

loop_sum:
ADD R1, R1, R2   ; R1 = R1 + R2   (sum += i)
ADD R2, R2, 1    ; R2 = R2 + 1    (i++)
BGT R2, R0, end_sum  ; if i > N jump to end_sum
JMP loop_sum

end_sum:
STR R1, 1        ; RAM[1] <- sum

; --- Exemple d'opérations supplémentaires: DIV et MOD ---
MOV R4, 7        ; diviseur = 7
DIV R5, R1, R4   ; R5 = R1 / 7   (quotient)
MOD R6, R1, R4   ; R6 = R1 % 7   (reste)
STR R5, 2        ; RAM[2] <- quotient
STR R6, 3        ; RAM[3] <- remainder

; --- Utilisation de BEQ pour tester divisibilité ---
MOV R7, 0
BEQ R6, R7, divisible   ; if remainder == 0 -> divisible
JMP not_divisible

divisible:
; action si divisible (ex: écrire 1 dans RAM[4])
MOV R7, 1
STR R7, 4
JMP done

not_divisible:
; action sinon (ex: écrire 0 dans RAM[4])
MOV R7, 0
STR R7, 4

done:
; Fin du programme