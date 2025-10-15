VAR SYS.OPR.TEMP
TAG :exponential_lib_IMPORT
SLF
CALL
SAY "Starting exponential calculations"
VAR A
VAR B
SET A, #1
SET B, #2
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
ADD A, #1
ADD B, #1
SET R0, A
SET R1, B
SAY "Result of {R0}^{R1} is :"
TAG :exponential_lib.POWER_FUNC
SLF
CALL
SAY "{R0}"
:exponential_lib_IMPORT
VAR SYS.OPR.TEMP
RET
:exponential_lib.POWER_FUNC
SUB R1, #1
SET R3 #0
SET R2 R0
GOTO :exponential_lib.POWER_LOOP
:exponential_lib.POWER_LOOP
SET SYS.OPR.TEMP R2
MUL SYS.OPR.TEMP R0
SET R2 SYS.OPR.TEMP
SUB R1, #1
IF R1 = R3 :exponential_lib.:POWER_RETURN
ELSE
CLR
GOTO :exponential_lib.POWER_LOOP
:exponential_lib.POWER_RETURN
SET R0, R2
RET