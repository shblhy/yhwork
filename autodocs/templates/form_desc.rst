* 接口参数
.. code-block:: json

    {
    	{%for field in field_list%}{{field.key}}: {{field.label}}  {{field.is_required}} {{field.desc}}
    	{%endfor%}
    }
