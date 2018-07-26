set nu
syntax on
set ts=4
set shiftwidth=4
set ff=unix
set viminfo='1000,<500
" set expandtab
" set autoindent

if has("autocmd")
  au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
endif
