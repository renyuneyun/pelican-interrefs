Pelican Inter References: A Plugin for Pelican
====================================================

[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/pelican-interrefs/build)](https://github.com/pelican-plugins/pelican-interrefs/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-interrefs)](https://pypi.org/project/pelican-interrefs/)
![License](https://img.shields.io/pypi/l/pelican-interrefs?color=blue)

Obtain inter-references (both forward and backward) of each article. The interrefs are links between articles on the same site (rather than arbitrary links on the Web).

Note: Part of the information in this file is auto-generated. They may not work or correctly reflect the current status.

Installation
------------

This plugin can be installed via:

    python -m pip install pelican-interrefs

Usage
-----

This plugin adds a `interrefs` field to the article object, which contains two other fields: `forward` and `backward`.

The `interrefs.forward` field contains all (articles of) the forward links that present in this article (i.e. links to another article from this article). Similarly, the `interrefs.backward` field contains all (articles of) the backward links to this article (i.e. links from another article to this article).

Specifically, `interrefs` will evaluate to `False` if both `forward` and `backward` are empty. This should make the template simpler.

The following settings are recognized:

- `FORWARD_REFS`: The number of forward links to have in the list
- `BACKWARD_REFS`: The number of backward links to have in the list

Note: The current implementation is not very efficient. The worst case complexity is `O(n^3)` where `n` is the number of articles.

### Template

You may use this piece of code for your template.

```
{% if article.interrefs %}
<div class="interrefs">
    {% if article.interrefs.forward %}
    <div class="forward_refs">
        <b>Forward links:</b>
        <ul>
        {% for post in article.interrefs.forward %}
            <li><a href="{{ SITEURL }}/{{ post.url }}">{{ post.title }}</a></li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
    {% if article.interrefs.backward %}
    <div class="backward_refs">
        <b>Backward links:</b>
        <ul>
        {% for post in article.interrefs.backward %}
            <li><a href="{{ SITEURL }}/{{ post.url }}">{{ post.title }}</a></li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>
{% endif %}
```

TODO
------------

* [ ] Support posts?
* [ ] Support i18n-subsites
* [ ] Optimize performance

Contributing
------------

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/pelican-plugins/pelican-interrefs/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html

License
-------

This project is licensed under the AGPL-3.0 license.
