.smc
.list
.dasm
.detect on
.echo
.org $08000
.asctable
" ".."~" = 64
.end

start:	clc		; set all cpu registers to zero
	xce
	rep #$ff
	lda #$1fff
	tcs
	lda #$000
	ldx #$000
	ldy #$000
	tcd
	pha
	plb
	plp
-	sta $000,x	; clear first 8k of mem
	inx
	inx
	cpx #$2000
	bne -
	jsr init	;setup regs
	jsr initmem	;clear memory
	jsr initcol	;clear colors
	jsr initvid	;clear vram
	jsr initoam	;clear oam

;evrything should be cleared now (i'm not bothering with the sound!)
	sep #$20
	jsr color	;setup colors
	jsr tile	;setup tile patterns
	jsr namet	;setup name table
	lda #$3		;set to mode 3
	sta $2105
	lda #$1		;setup main/sub
	sta $212c
	stz $212d
	stz $2130
	lda #$21
	sta $2131
	lda #$e0	;init color constant
	sta $2132

	lda #47		;setup green for hdma
	sta $800
	lda #$40
	sta $801
	ldx #$000
-	inc $802,x
	txa
	asl
	asl
	and #$18
	ora #$40
	sta $803,x
	inx
	inx
	cpx #$100
	bne -
	lda #$1
	sta $802,x
	lda #$40
	sta $803,x

	lda #47		;do red for hdma
	sta $980
	lda #$20
	sta $981
	ldx #$000
	ldy #$000
-	lda #$4
	sta $982,x
	tya
	and #$1f
	ora #$20
	sta $983,x
	inx
	inx
	iny
	cpy #$20
	bne -
	lda #$1
	sta $982,x
	lda #$20
	sta $983,x

	lda #$f		;do last video stuff
	sta $2100
	lda #$81
	sta $4200

kernal:	brl kernal	;enter eternal wait state


;the nmi is used mainly to update the video during the vblank
; all the rest is caculated after the interupt completes in the kernal
nmi:	rep #$30
	phy
	phx
	pha
	sep #$20
	stz $4300	;setup for green hdma
	lda #$32
	sta $4301
	ldx #$800
	stx $4302
	stz $4304
	stz $4310	;setup for red hdma
	lda #$32
	sta $4311
	ldx #$980
	stx $4312
	stz $4314
	lda #$3		;start the hdma
	sta $420c
	rep #$30
	pla
	plx
	ply	
	rti		
.mem 8

namet:	ldx #$400
	stx $2116
	ldx #$000
	ldy #$0ff
-	sty $2118
	inx
	cpx #$400
	bne -
	ldx #$4c0
	stx $2116
	rep #$20
	ldx #$000
-	txa
	and #$01f
	sta $2118
	inx
	cpx #$200
	bne -
	sep #$20
	lda #$4
	sta $2107
	rts

.index 8
tconv:	ldx #$0		;move 00 to 40
-	lda $1000,x
	sta $1040,x
	inx
	cpx #$40
	bne -
	ldx #$0		;conv packed 40 to planar at 80
	ldy #$0
--	lda #$8
	sta $0
-	lsr $1040,x
	lda $1080,y
	rol
	sta $1080,y
	inx
	dec $0
	bne -
	txa
	and #$3f
	tax
	iny
	cpy #$40
	bne --
	ldx #$0		;conv from planar at 80 to interleaved at c0
-	txa
	and #$30
	sta $0
	txa
	asl
	and #$e
	ora $0
	sta $0
	txa
	lsr
	lsr
	lsr
	and #$1
	ora $0
	tay
	lda $1080,x
	sta $10c0,y
	inx
	cpx #$40
	bne -
	rts

.index 16
tile:	ldx #$000	init for last 8 colors
-:	txa
	and #$7
	ora #$f8
	sta $1000,x
	inx
	cpx #$040
	bne -
	lda #$80	;init vram addr
	sta $2115
	stz $2116
			
	ldy #$000	;counter for tiles 0-31

--	ldx #$000	;add 8 to cols
-	lda $1000,x
	clc
	adc #$8
	sta $1000,x
	inx
	cpx #$040
	bne -

	phy
	sep #$10
	jsr tconv	;convert to planar format
	rep #$30
	ply

	ldx #$000	;move tile to vram
-	lda $10c0,x
	sta $2118
	inx
	inx
	cpx #$040
	bne -
	sep #$20
	iny
	cpy #$020
	bne --
	rts

color:	ldx #$000
	ldy #$000
-	tya
	and #$e0
	sta $200,x
	tya
	and #$1f
	asl
	asl
	sta $201,x
	inx
	inx
	iny
	cpy #$100
	bne -
	stz $2121	;Move colors to CRAM
	ldx #$000
-	lda $200,x
	sta $2122
	inx
	cpx #$200
	bne -
	rts

;------------------------------ init subroutines ---------------------------------

; most of the below init subroutine wan't my own work, :\ sorry to whoever's code it was that i ripped! :)
init:	php                             ; Save registers used.
	sep #$20
	pha                             ; Save processor status.
	lda     #$8f                    ; Screen off, full brightness.
	sta     $2100                   ; Store to screen register.
	stz     $2101                   ; sprite register (size + address in VRAM)
	stz     $2102                   ; sprite registers (address of sprite memory [OAM])
	stz     $2103                   ; "
	stz     $2105                   ; set graphics Mode 0
	stz     $2106                   ; no planes, no mosiac
	stz     $2107                   ; plane 0 map VRAM location ($0000 vram)
	stz     $2108                   ; plane 1 map VRAM location
	stz     $2109                   ; plane 2 "
	stz     $210a                   ; plane 3 "
	stz     $210b                   ; plane 0+1 tile data location
	stz     $210c                   ; plane 0+2 "
	stz     $210d                   ; plane 0 scroll x (first 8 bits)
	stz     $210d                   ; plane 0 scroll x (last 3 bits) write to reg twice
	stz     $210e                   ; plane 0 scroll y "
	stz     $210e                   ; plane 0 scroll y "
	stz     $210f                   ; plane 1 scroll x (first 8 bits)
	stz     $210f                   ; plane 1 scroll x (last 3 bits) write to reg twice
	stz     $2110                   ; plane 1 scroll y "
	stz     $2110                   ; plane 1 scroll y "
	stz     $2111                   ; plane 2 scroll x (first 8 bits)
	stz     $2111                   ; plane 2 scroll x (last 3 bits) write to reg twice
	stz     $2112                   ; plane 2 scroll y "
	stz     $2112                   ; plane 2 scroll y "
	stz     $2113                   ; plane 3 scroll x (first 8 bits)
	stz     $2113                   ; plane 3 scroll x (last 3 bits) write to reg twice
	stz     $2114                   ; plane 3 scroll y "
	stz     $2114                   ; plane 3 scroll y "
	lda     #$80                    ; increase VRAM after writes to $2118.19
	sta     $2115                   ; store to VRAM increment register
	stz     $2116                   ; VRAM address low
	stz     $2117                   ; VRAM address hi
	stz     $211a                   ; init mode 7 setting reg
	stz     $211b                   ; mode 7 matrix parameter A register (low)
	stz     $211b                   ; Mode 7 matrix parameter A register (low)
	lda     #$01
	sta     $211b                   ; Mode 7 matrix parameter A register (high)
	stz     $211c                   ; Mode 7 matrix parameter B register (low)
	stz     $211c                   ; Mode 7 matrix parameter B register (high)
	stz     $211d                   ; Mode 7 matrix parameter C register (low)
	stz     $211d                   ; Mode 7 matrix parameter C register (high)
	stz     $211e                   ; Mode 7 matrix parameter D register (low)
	lda     #$01
	sta     $211e                   ; Mode 7 matrix parameter D register (high)
	stz     $211f                   ; Mode 7 center position X register (low)
	stz     $211f                   ; Mode 7 center position X register (high)
	stz     $2120                   ; Mode 7 center position Y register (low)
	stz     $2120                   ; Mode 7 center position Y register (high)
	stz     $2121                   ; Color number register ($0-ff)
	stz     $2123                   ; BG1 & BG2 Window mask setting register
	stz     $2124                   ; BG3 & BG4 Window mask setting register
	stz     $2125                   ; OBJ & Color Window mask setting register
	stz     $2126                   ; Window 1 left position register
	stz     $2127                   ; Window 2 left position register
	stz     $2128                   ; Window 3 left position register
	stz     $2129                   ; Window 4 left position register
	stz     $212a                   ; BG1, BG2, BG3, BG4 Window Logic register
	stz     $212b                   ; OBJ, Color Window Logic Register (or,and,xor,xnor)
	stz     $212c                   ; Main Screen designation (planes, sprites enable)
	stz     $212d                   ; Sub Screen designation
	stz     $212e                   ; Window mask for Main Screen
	stz     $212f                   ; Window mask for Sub Screen
	lda     #$30
	sta     $2130                   ; Color addition & screen addition init setting
	stz     $2131                   ; Add/Sub sub designation for screen, sprite, color
	lda     #$e0
	sta     $2132                   ; color data for addition/subtraction
	stz     $2133                   ; Screen setting (interlace x,y/enable SFX data)
	stz     $4200                   ; Enable V-blank, interrupt, Joypad register
	lda     #$ff
	stz     $4201                   ; Programmable I/O port
	stz     $4202                   ; Multiplicand A
	stz     $4203                   ; Multiplier B
	stz     $4204                   ; Multiplier C
	stz     $4205                   ; Multiplicand C
	stz     $4206                   ; Divisor B
	stz     $4207                   ; Horizontal Count Timer
	stz     $4208                   ; Horizontal Count Timer MSB (most significant bit)
	stz     $4209                   ; Vertical Count Timer
	stz     $420a                   ; Vertical Count Timer MSB
	stz     $420b                   ; General DMA enable (bits 0-7)
	stz     $420c                   ; Horizontal DMA (HDMA) enable (bits 0-7)
	stz     $420d                   ; Access cycle designation (slow/fast rom)
	pla                             ; Restore processor status.
	plp                             ; Restore all registers.
	rts

;now, back to my own work! =)
initmem: php
	rep #$30
	pha
	phx
	lda #$000
	ldx #$2000
-	sta $7E0000,x	;clear last 56k of 1st ram bank
	inx
	inx
	bne -
-	sta $7F0000,x	;clear last 64k of mem
	inx
	inx
	bne -
	plx
	pla
	plp
	rts

initcol: php
	rep #$30
	pha
	phx
	sep #$20
	lda #$0
	sta $2121
	ldx #$200
-	sta $2122
	dex
	bne -
	plx
	rep #$20
	pla
	plp
	rts

initvid: php
	rep #$30
	pha
	phx
	lda #$000
	ldx #$000
	sta $2116
	sta $2117
-	sta $2118
	inx
	inx
	bne -
	plx
	pla
	plp
	rts

initoam: php
	rep #$10
	pha
	phx
	lda #$0
	sta $2102
	lda #$0
	sta $2103
	ldx #$220
	lda #$0
-	sta $2104
	dex
	bne -
	plx
	pla
	plp
	rts

.cartridge
   title           =       "32,768 color demo"
   mode            =       $20
   type            =       $00
   romsize         =       $00
   ramsize         =       $00
   country         =       $00
   maker           =       $00
   version         =       $00
.end

.pad $ffea
	.dw nmi

.pad $fffc
	.dw start,$000
