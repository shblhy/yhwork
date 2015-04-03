* 返回数据 (状态码：200)

.. code-block:: json
	
	数据格式：
	{{output_str|safe}}
	行内容描述：
	[{%for field,label in field_list%}{{field}}:{{label}}， {%if forloop.counter|divisibleby:5%}
	{%endif%}{%endfor%}]
    