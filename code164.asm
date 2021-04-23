section .text
_main:
mov rdx, 10
mov rbx, 10
mov rsi, rdx
add rsi, rbx
mov r8, rsi
mov rdi, rdx
add rdi, rbx
mov r9, rdi
push rcx
mov rcx, r9
call __ZN6System3out7printlnEi
pop rcx
mov rax, 0
ret

section .data
