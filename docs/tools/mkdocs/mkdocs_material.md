# Material for MkDocs

> - [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

material 是 mkdocs 的一个主题，提供多种配置选项，这里记录如何开启并利用一些特性。

## Setup

主要是主题配置和插件支持。

```yaml
extra_javascript:
  - "https://cdnjs.loli.net/ajax/libs/pangu/3.3.0/pangu.min.js"
  - "static/js/extra.js"
  - "https://cdnjs.loli.net/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-MML-AM_CHTML"
extra_css:
  - "static/css/extra.css"
theme:
  name: material
  language: zh
  palette:
    - scheme: default
      primary: teal
      accent: red
      toggle:
        icon: material/toggle-switch-off-outline
        name: Switch to dark mode
    - scheme: slate
      primary: red
      accent: red
      toggle:
        icon: material/toggle-switch
        name: Switch to light mode
  icon:
    repo: fontawesome/brands/github-alt
  logo: static/githubcat.jpg
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - search.suggest
    - search.highlight
    - search.share
  font:
    text: "Noto Sans"
    code: "Source Code Pro"
plugins:
  - search
  - git-revision-date-localized
  - minify:
      minify_html: true  
```

## Markdown Extensions

mkdocs 基于 [Python Markdown](https://python-markdown.github.io/) 解析 markdown，后者为标准 markdown 提供了扩展。

[pymdown-extensions](https://facelessuser.github.io/pymdown-extensions/) 为 Python Markdown 提供更多的扩展功能。

都要在 *mkdocs.yml* 中开启。

```yaml
markdown_extensions:
  - admonition
  - md_in_html
  - codehilite:
      linenums: true
      guess_lang: false
  - def_list
  - footnotes
  - meta
  - toc:
      permalink: "*"
  - pymdownx.arithmatex
  - pymdownx.caret
  - pymdownx.critic
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji ""
      emoji_generator: !!python/name:materialx.emoji.to_svg ""
  - pymdownx.highlight      
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format ""  
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.tilde
```

### Abbreviations 缩写

开启缩写支持：

```yaml
makrdown_extensions:
  - abbr
  - pymdownx.snippets
```

markdown 语法：

```mark
The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium
```

渲染结果：

The HTML specification is maintained by the W3C. 

*[HTML]: Hyper Text Markup Language 
*[W3C]: World Wide Web Consortium

可以配合 `pymdownx.snippets` 实现整个项目的术语表，snippets 就是将一个另外的 markdown 文件嵌入到本文件中。

markdown 语法：

```markdown
--8<-- "filename.ext"
```

### Admonitions 警告

其实就是文档的提示块，开启支持：

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
```

markdown 语法：

```markdown
!!! note "Title"

	  This is a note.
```

渲染结果：

!!! note "Title"

    This is a note.

开启 `pymdownx.details` 后支持可折叠的提示块，将 `!!!` 换成 `???` 即可。

```markdown
??? note "可折叠块"

    这是一个可折叠块。
```

??? note "可折叠块"

    这是一个可折叠块。

使用 `???+` 设置为默认展开。

???+ note "展开的可折叠块"

    这是一个展开的可折叠块。

甚至还可以渲染行内块:

=== "inline"

    Result/Example:

    !!! info inline

        This is a inline block left. 

    ```markdown
    !!! info inline

        This is a inline block left
    ```

=== "inline end"

    Example/Result:

    !!! info inline end

        This is a inline block right.

    ```markdown
    !!! info inline end

        This is a inline block right.
    ```

Magic!

支持多种提示块的标识符：note, abstract/summary/tldr, info/todo, tip/hint/important, success/check/done, question/help/faq, warning/caution/attention, failure/fail/missing, danger/error, bug, example, quote/cite

`note`

:   !!! note

        This is a note.

`abstract`, `summary`, `tldr`

:   !!! abstract

        This is a abstract.

`info`, `todo`

:   !!! info

        This is a info.

`tip`, `hint`, `important`

:   !!! tip

        This is a tip.

`success`, `check`, `done`

:   !!! success

        This is a success.

`question`, `help`, `faq`

:   !!! question

        This is a question.

`warning`, `caution`, `attention`

:   !!! warning

        This is a warning.

`failure`, `fail`, `missing`

:   !!! failure

        This is a failure.

`danger`, `error`

:   !!! danger

        This is a danger.

`bug`

:   !!! bug

        This is a bug.

`example`

:   !!! example

        This is a example.

`quote`, `cite`

:   !!! quote

        This is a quote.

甚至可以自定义一个提示块类型，指定一个颜色和一个 svg 图标。


<style>
  :root {
  --md-admonition-icon--pied-piper: url('data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><path d="M244 246c-3.2-2-6.3-2.9-10.1-2.9-6.6 0-12.6 3.2-19.3 3.7l1.7 4.9zm135.9 197.9c-19 0-64.1 9.5-79.9 19.8l6.9 45.1c35.7 6.1 70.1 3.6 106-9.8-4.8-10-23.5-55.1-33-55.1zM340.8 177c6.6 2.8 11.5 9.2 22.7 22.1 2-1.4 7.5-5.2 7.5-8.6 0-4.9-11.8-13.2-13.2-23 11.2-5.7 25.2-6 37.6-8.9 68.1-16.4 116.3-52.9 146.8-116.7C548.3 29.3 554 16.1 554.6 2l-2 2.6c-28.4 50-33 63.2-81.3 100-31.9 24.4-69.2 40.2-106.6 54.6l-6.3-.3v-21.8c-19.6 1.6-19.7-14.6-31.6-23-18.7 20.6-31.6 40.8-58.9 51.1-12.7 4.8-19.6 10-25.9 21.8 34.9-16.4 91.2-13.5 98.8-10zM555.5 0l-.6 1.1-.3.9.6-.6zm-59.2 382.1c-33.9-56.9-75.3-118.4-150-115.5l-.3-6c-1.1-13.5 32.8 3.2 35.1-31l-14.4 7.2c-19.8-45.7-8.6-54.3-65.5-54.3-14.7 0-26.7 1.7-41.4 4.6 2.9 18.6 2.2 36.7-10.9 50.3l19.5 5.5c-1.7 3.2-2.9 6.3-2.9 9.8 0 21 42.8 2.9 42.8 33.6 0 18.4-36.8 60.1-54.9 60.1-8 0-53.7-50-53.4-60.1l.3-4.6 52.3-11.5c13-2.6 12.3-22.7-2.9-22.7-3.7 0-43.1 9.2-49.4 10.6-2-5.2-7.5-14.1-13.8-14.1-3.2 0-6.3 3.2-9.5 4-9.2 2.6-31 2.9-21.5 20.1L15.9 298.5c-5.5 1.1-8.9 6.3-8.9 11.8 0 6 5.5 10.9 11.5 10.9 8 0 131.3-28.4 147.4-32.2 2.6 3.2 4.6 6.3 7.8 8.6 20.1 14.4 59.8 85.9 76.4 85.9 24.1 0 58-22.4 71.3-41.9 3.2-4.3 6.9-7.5 12.4-6.9.6 13.8-31.6 34.2-33 43.7-1.4 10.2-1 35.2-.3 41.1 26.7 8.1 52-3.6 77.9-2.9 4.3-21 10.6-41.9 9.8-63.5l-.3-9.5c-1.4-34.2-10.9-38.5-34.8-58.6-1.1-1.1-2.6-2.6-3.7-4 2.2-1.4 1.1-1 4.6-1.7 88.5 0 56.3 183.6 111.5 229.9 33.1-15 72.5-27.9 103.5-47.2-29-25.6-52.6-45.7-72.7-79.9zm-196.2 46.1v27.2l11.8-3.4-2.9-23.8zm-68.7-150.4l24.1 61.2 21-13.8-31.3-50.9zm84.4 154.9l2 12.4c9-1.5 58.4-6.6 58.4-14.1 0-1.4-.6-3.2-.9-4.6-26.8 0-36.9 3.8-59.5 6.3z"/></svg>')
}
.md-typeset .admonition.pied-piper,
.md-typeset details.pied-piper {
  border-color: rgb(43, 155, 70);
}
.md-typeset .pied-piper > .admonition-title,
.md-typeset .pied-piper > summary {
  background-color: rgba(43, 155, 70, 0.1);
  border-color: rgb(43, 155, 70);
}
.md-typeset .pied-piper > .admonition-title::before,
.md-typeset .pied-piper > summary::before {
  background-color: rgb(43, 155, 70);
  -webkit-mask-image: var(--md-admonition-icon--pied-piper);
          mask-image: var(--md-admonition-icon--pied-piper);
}

</style>

=== "example"

    ```markdwon
    !!! pied-piper "Pied Piper"

        This is a pied-piper.
    ```

=== "docs/static/extra.css"

    ```css
    :root {
      --md-admonition-icon--pied-piper: url('data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><path d="M244 246c-3.2-2-6.3-2.9-10.1-2.9-6.6 0-12.6 3.2-19.3 3.7l1.7 4.9zm135.9 197.9c-19 0-64.1 9.5-79.9 19.8l6.9 45.1c35.7 6.1 70.1 3.6 106-9.8-4.8-10-23.5-55.1-33-55.1zM340.8 177c6.6 2.8 11.5 9.2 22.7 22.1 2-1.4 7.5-5.2 7.5-8.6 0-4.9-11.8-13.2-13.2-23 11.2-5.7 25.2-6 37.6-8.9 68.1-16.4 116.3-52.9 146.8-116.7C548.3 29.3 554 16.1 554.6 2l-2 2.6c-28.4 50-33 63.2-81.3 100-31.9 24.4-69.2 40.2-106.6 54.6l-6.3-.3v-21.8c-19.6 1.6-19.7-14.6-31.6-23-18.7 20.6-31.6 40.8-58.9 51.1-12.7 4.8-19.6 10-25.9 21.8 34.9-16.4 91.2-13.5 98.8-10zM555.5 0l-.6 1.1-.3.9.6-.6zm-59.2 382.1c-33.9-56.9-75.3-118.4-150-115.5l-.3-6c-1.1-13.5 32.8 3.2 35.1-31l-14.4 7.2c-19.8-45.7-8.6-54.3-65.5-54.3-14.7 0-26.7 1.7-41.4 4.6 2.9 18.6 2.2 36.7-10.9 50.3l19.5 5.5c-1.7 3.2-2.9 6.3-2.9 9.8 0 21 42.8 2.9 42.8 33.6 0 18.4-36.8 60.1-54.9 60.1-8 0-53.7-50-53.4-60.1l.3-4.6 52.3-11.5c13-2.6 12.3-22.7-2.9-22.7-3.7 0-43.1 9.2-49.4 10.6-2-5.2-7.5-14.1-13.8-14.1-3.2 0-6.3 3.2-9.5 4-9.2 2.6-31 2.9-21.5 20.1L15.9 298.5c-5.5 1.1-8.9 6.3-8.9 11.8 0 6 5.5 10.9 11.5 10.9 8 0 131.3-28.4 147.4-32.2 2.6 3.2 4.6 6.3 7.8 8.6 20.1 14.4 59.8 85.9 76.4 85.9 24.1 0 58-22.4 71.3-41.9 3.2-4.3 6.9-7.5 12.4-6.9.6 13.8-31.6 34.2-33 43.7-1.4 10.2-1 35.2-.3 41.1 26.7 8.1 52-3.6 77.9-2.9 4.3-21 10.6-41.9 9.8-63.5l-.3-9.5c-1.4-34.2-10.9-38.5-34.8-58.6-1.1-1.1-2.6-2.6-3.7-4 2.2-1.4 1.1-1 4.6-1.7 88.5 0 56.3 183.6 111.5 229.9 33.1-15 72.5-27.9 103.5-47.2-29-25.6-52.6-45.7-72.7-79.9zm-196.2 46.1v27.2l11.8-3.4-2.9-23.8zm-68.7-150.4l24.1 61.2 21-13.8-31.3-50.9zm84.4 154.9l2 12.4c9-1.5 58.4-6.6 58.4-14.1 0-1.4-.6-3.2-.9-4.6-26.8 0-36.9 3.8-59.5 6.3z"/></svg>')
    }
    .md-typeset .admonition.pied-piper,
    .md-typeset details.pied-piper {
      border-color: rgb(43, 155, 70);
    }
    .md-typeset .pied-piper > .admonition-title,
    .md-typeset .pied-piper > summary {
      background-color: rgba(43, 155, 70, 0.1);
      border-color: rgb(43, 155, 70);
    }
    .md-typeset .pied-piper > .admonition-title::before,
    .md-typeset .pied-piper > summary::before {
      background-color: rgb(43, 155, 70);
      -webkit-mask-image: var(--md-admonition-icon--pied-piper);
              mask-image: var(--md-admonition-icon--pied-piper);
    }

    ```

=== "mkdocs.yml"

    ```yaml
    extra_css:
      - static/extra.css
    ```

!!! pied-piper

    This is a pied-piper.

### Code blocks 代码块

包括语法高亮、嵌套代码块、snippets 等功能，开启支持：

```yaml
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.superfences
  - pymdownx.snippets
```

支持给代码块添加标题、添加行内注释（8.0.0b1 的特性，还不能用）、行号（甚至支持不从 1 开始）、高亮选中行。

markdown 语法：

````markdown
```yaml title="yaml" linenums="2" hl_lines="1 2"
theme:
  features:
    - content.code.annotate # (1)
```

1.  :This is a comment
````

渲染结果：

```yaml title="yaml" linenums="2" hl_lines="1 2"
theme:
  features:
    - content.code.annotate # (1)
```

1.  :This is a comment

### Content tabs 标签

开启支持：

```yaml
markdown_extensions:
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true 
```

支持组合代码块。

markdown 语法：

````markdown
=== "C"

    ```c
    #include<stdio.h>

    int main() {
      printf("Hello World!\n");
      return 0;
    }
    ```

=== "C++"

    ```c++
    #include<iostream>

    int main() {
      std::cout << "Hello World!" << std::endl;
      return 0;
    }
    ```
````

渲染结果：

=== "C"

    ```c
    #include<stdio.h>

    int main() {
      printf("Hello World!\n");
      return 0;
    }
    ```

=== "C++"

    ```c++
    #include<iostream>

    int main() {
      std::cout << "Hello World!" << std::endl;
      return 0;
    }
    ```

开启 `pymdownx.superfence` 之后，块之间随意嵌套。

````markdown
!!! example

    === "Unordered List"

        _Example_:

        ``` markdown
        * Sed sagittis eleifend rutrum
        * Donec vitae suscipit est
        * Nulla tempor lobortis orci
        ```

        _Result_:

        * Sed sagittis eleifend rutrum
        * Donec vitae suscipit est
        * Nulla tempor lobortis orci

    === "Ordered List"

        _Example_:

        ``` markdown
        1. Sed sagittis eleifend rutrum
        2. Donec vitae suscipit est
        3. Nulla tempor lobortis orci
        ```

        _Result_:

        1. Sed sagittis eleifend rutrum
        2. Donec vitae suscipit est
        3. Nulla tempor lobortis orci

````

!!! example

    === "Unordered List"

        _Example_:

        ``` markdown
        * Sed sagittis eleifend rutrum
        * Donec vitae suscipit est
        * Nulla tempor lobortis orci
        ```

        _Result_:

        * Sed sagittis eleifend rutrum
        * Donec vitae suscipit est
        * Nulla tempor lobortis orci

    === "Ordered List"

        _Example_:

        ``` markdown
        1. Sed sagittis eleifend rutrum
        2. Donec vitae suscipit est
        3. Nulla tempor lobortis orci
        ```

        _Result_:

        1. Sed sagittis eleifend rutrum
        2. Donec vitae suscipit est
        3. Nulla tempor lobortis orci

### Footnotes 脚注

开启支持：

```yaml
markdown_extensions:
  - footnotes
```

markdown 语法：

```markdown
This is a foodnote[^1][^2].

[^1]: This is a foodnote.
[^2]:
    This is a multiline
    foodnote.
```

渲染结果：

This is a foodnote[^1][^2].

[^1]: This is a foodnote.
[^2]:
    This is a multiline
    foodnote.

### Formatting 格式化

开启支持：

```yaml
markdown_extensions:
  - pymdownx.critic
  - pymdownx.caret
  - pymdownx.keys
  - pymdownx.mark
  - pymdownx.tilde
```

开启 `pymdownx.critic` 之后，支持高亮修改或者添加一段 inline 注释。

markdown 语法：

````markdown
Text can be {`--`deleted`--`} and replacement text {`++`added`++`}. This can also be
combined into {`~~`one`~>`a single`~~`} operation. {`==`Highlighting`==`} is also
possible {`>>`and comments can be added inline`<<`}.

{`==`

Formatting can also be applied to blocks by putting the opening and closing
tags on separate lines and adding new lines between the tags and the content.

`==`}
````

渲染结果：

Text can be {--deleted--} and replacement text {++added++}. This can also be
combined into {~~one~>a single~~} operation. {==Highlighting==} is also
possible {>>and comments can be added inline<<}.

{==

Formatting can also be applied to blocks by putting the opening and closing
tags on separate lines and adding new lines between the tags and the content.

==}

!!! bug "Bug"

    这部不知道是为什么代码块里的语法也被渲染了。。。这里把符号围起来才能看到原始的。

还支持另外一种高亮、下划线和删除方式。

markdown 语法：

```markdown
- ==This was marked==
- ^^This was inserted^^
- ~~This was deleted~~
```

渲染结果

- ==This was marked==
- ^^This was inserted^^
- ~~This was deleted~~

### Icons + Emojis 图标和表情

<div class="mdx-iconsearch" data-mdx-component="iconsearch">
  <input
    class="md-input md-input--stretch mdx-iconsearch__input"
    placeholder="Search the icon and emoji database"
    data-mdx-component="iconsearch-query"
  />
  <div class="mdx-iconsearch-result" data-mdx-component="iconsearch-result">
    <div class="mdx-iconsearch-result__meta"></div>
    <ol class="mdx-iconsearch-result__list"></ol>
  </div>
</div>

???+ tip "Tips"

    输入关键词可以搜索图标和表情。

开启支持：

```yaml
markdown_extensions:
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
```

支持图标和标签，集成了 [Material Design](https://materialdesignicons.com/), [FontAwesome](https://fontawesome.com/icons?d=gallery&m=free), [Octicons](https://octicons.github.com/) 图标库。

markdown 语法：

```markdown
:smile:

:material-account-circle: - `material/account-circle.svg`
```

渲染结果：

:smile:

:material-account-circle: - `material/account-circle.svg`

### Images 图像

开启支持：

```yaml
markdown_extensions:
  - attr_list
  - md_in_html
```

支持图片靠左或右对齐。

=== "left"

    markdown 语法：

    ```markdown
    ![](https://dummyimage.com/600x400/eee/aaa){ align=left width=300}
    ```

    渲染结果：

    ![](https://dummyimage.com/600x400/eee/aaa){ align=left width=300}

    这是一张图片。

=== "right"
    
    markdown 语法：

    ```markdown
    ![](https://dummyimage.com/600x400/eee/aaa){ align=right width=300}
    ```

    渲染结果：

    ![](https://dummyimage.com/600x400/eee/aaa){ align=right width=300}

    这是一张图片。


markdown 不支持图像标题，使用 html figure 和 figcaption 标签。

markdown 语法：

```markdown
<figure markdown>
  ![Dummy image](https://dummyimage.com/600x400/){ width="300" }
  <figcaption>图片标题</figcaption>
</figure>
```

渲染结果：

<figure markdown>
  ![Dummy image](https://dummyimage.com/600x400/){ width="300" }
  <figcaption>图片标题</figcaption>
</figure>

使用 `{loading=lazy}` 可以设置图片延迟加载。

### Lists 列表

开启支持：

```yaml
markdown_extensions:
  - def_list
  - pymdownx.tasklist:
      custom_checkbox: true
```

开启 `def_list` 后，支持创建任意键值对的列表。

markdown 语法：

```markdown
`definition`

:   description
```

渲染结果：

`definition`

:   description

### MathJax

开启 latex 支持：

=== "docs/static/extra.js"

    ```js
    window.MathJax = {
      tex: {
        inlineMath: [["\\(", "\\)"]],
        displayMath: [["\\[", "\\]"]],
        processEscapes: true,
        processEnvironments: true
      },
      options: {
        ignoreHtmlClass: ".*|",
        processHtmlClass: "arithmatex"
      }
    };

    document$.subscribe(() => {
      MathJax.typesetPromise()
    })
    ```

=== "mkdocs.yml"

    ```yaml
    markdown_extensions:
      - pymdownx.arithmatex:
          generic: true

    extra_javascript:
      - javascripts/mathjax.js
      - https://polyfill.io/v3/polyfill.min.js?features=es6
      - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
    ```