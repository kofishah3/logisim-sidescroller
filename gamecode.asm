; ========================================
; SIMPLE FISH GAME - Basic Flow
; ========================================

; Start at address 0 - Wait for start button
ORG 0
WAIT_FOR_START:
    IN 1                   ; Read start button (port 0)
    CMP 1                  ; Check if button pressed (value 1)
    JEQ INITIALIZE_GAME    ; If pressed, start game
    JMP WAIT_FOR_START     ; Keep waiting for button press

; Initialize game when start button pressed
ORG 5
INITIALIZE_GAME:
    START_GAME                ; Set initial player Y position (middle position)
    ; Player Y position now stored in register
    JMP GAME_LOOP          ; Jump to main game loop

; ========================================
; MAIN GAME LOOP - Address 10
; ========================================
ORG 10
GAME_LOOP:
    SPAWN_OBSTACLE            ; Spawn new obstacle
    SCORE_INCREMENT        ; Increase score
    
    ; Check for player input (always allow movement)
    IN 2                   ; Read movement controls (port 1)
    CMP 1                  ; Check if UP button pressed
    JEQ MOVE_PLAYER_UP     ; Move up if pressed
    CMP 2                  ; Check if DOWN button pressed
    JEQ MOVE_PLAYER_DOWN   ; Move down if pressed
    
    ; No input pressed, continue loop
    JMP GAME_LOOP          ; Back to start of loop

; Handle UP movement
MOVE_PLAYER_UP:
    MOVE_UP                ; Execute move up command
    JMP GAME_LOOP          ; Back to game loop

; Handle DOWN movement  
MOVE_PLAYER_DOWN:
    MOVE_DOWN              ; Execute move down command
    JMP GAME_LOOP          ; Back to game loop
