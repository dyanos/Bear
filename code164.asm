section .text
_main:
mov rsi, 10
mov rdx, 10
mov rbx, rsi
add rbx, rdx
mov rdi, rbx
push rcx
mov rcx, rdi
call ?println@out@System@@YAXPEBDZZ
pop rcx
mov rax, 0
ret

section .data
