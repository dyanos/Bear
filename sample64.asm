section .text
_Z3addi:
push rcx
mov rcx, rbx
push rdx
mov rdx, 4
call _Zplii
pop rdx
pop rcx
mov rax, rax
ret

_Z3addii:
push rcx
mov rcx, rsi
push rdx
mov rdx, rbx
call _Zplii
pop rdx
pop rcx
mov rax, rax
ret

section .data
