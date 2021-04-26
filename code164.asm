section .text
_main:
mov r8, 10
mov rsi, 10
mov rbx, r8
add rbx, rsi
mov rdi, rbx
push rcx
mov rcx, "%d"
push rdx
mov rdx, rdi
call ?println@out@System@@YAXPEADZZ
pop rdx
pop rcx
mov rax, 0
ret

section .data
