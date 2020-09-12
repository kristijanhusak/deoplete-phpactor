# deoplete-phpactor
[Phpactor](https://github.com/phpactor/phpactor) integration for [deoplete.nvim](https://github.com/Shougo/deoplete.nvim)


## Installation

Using [vim-plug](https://github.com/junegunn/vim-plug)

```
Plug 'Shougo/deoplete.nvim'
Plug 'phpactor/phpactor' ,  {'do': 'composer install', 'for': 'php'}
Plug 'kristijanhusak/deoplete-phpactor'
```

If you are using a custom setting for sources in deoplete don't forget:
```
call deoplete#custom#option('sources', {'php' : ['omni', 'phpactor', 'ultisnips', 'buffer']})
```

Add the phpactor source is important or phpactor itself is not running.
