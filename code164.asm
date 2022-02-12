section .text
_main:
mov [rbp + 16], 10
mov rbx, 10
mov r11, [rbp + 16]
add r11, rbx
mov rdi, r11
mov [rbp + 8], rdi
mov rsi, [rbp + 16]
mul rsi, rbx
mov [rbp + 0], rsi
mov r8, [rbp + 0]
mov r13, [rbp + 16]
div r13, rbx
mov r9, r13
mov r15, r9
push rax
push rcx
mov rcx, 1
push rdx
mov rdx, 3
call __ZN6System4lang5Array7toRangeEii
pop rdx
pop rcx
mov r10, rax
pop rax
mov r14, r10
mov r15, [rbp + 8]
mov [rbp + 24], [rbp + 16]
add [rbp + 24], rbx
mov r12, [rbp + 24]
push rcx
mov rcx, "%d"
push rdx
mov rdx, r12
call ?println@out@System@@YAXPEADZZ
pop rdx
pop rcx
mov rax, 0
ret

section .data
