django扩展
基于django 1.4.1开发，测试在1.4~1.7的django上均可用。
1、ListManager：
后台研发时发现，内容（Model）有限，而内容提取方式无限。如何用尽可能精简的代码，做到产生无穷格式的数据呢？

以下是我的思路：
	页面或者别的前端的诸多形式控件，只不过是以稍稍变化的方式重复同一种内容。使用类的继承重用，可以达成良好的代码复用效果。
	将数据理解为一个表格（代码中用Row描述），每行是一个记录（Line），每个属性则是一个单元格（Field）

单元格/Field处理：
	accessor 转化器 传入Model x，value = accessor(x)
	默认转化：accessor = getattr(x,field)，field 'attr1'将获取到值 value = x.attr1。 
	自定义转化： accessor = lambda x:x.func() 或 accessor = lambda x:func(..)

行/Line处理：
	构造表格时，用一个Model对应一个Line。
	fields    记录了Line上的所有Field
	accessors   accessor集合，记录了每个Field的取值方式
	accessors_out  accessors_out用于处理参数不仅是一个Model时的情况
	例如:
	class A(BaseListManager):
		fields [a,b,c]
		accessors = {
			a = lambda x:x.a+1,
			b = lambda x:x.a+x.b,
			c = BaseListManager.ACCESSORS_OUT,
		}
	A(
		accessors_out = lambda x: x.a if request.user.is_superuser else ''
	)
	调用get_line方法【def get_line(self, item, excludes=[])】，可利用model，获得每个line。excludes指不需要某个field。
	
表/Row处理:
	get_rows_data 代码就一句：[self.get_line(item) for item in models]

重构行级别处理：
	重写get_line()方法，get_rows_data将会调用此方法。
重构表级别处理：
	重写get_rows_data方法。

代码复用示例：
	1、构造最通用内容最详实的列表管理器OrderListManager，提供了订单列表的数据。
	2、新需求：失败订单列表，减少了状态status 成功/失败 这一列，要求不提供这样一列数据。
	    这时你可以这样做：
		用类FailedOrderListManager继承OrderListManager，重写get_line方法，excludes为[status]即可。如下：
		class FailedOrderListManager(OrderListManager):
			def get_line(self):
				return OrderListManager.get_line(self, exludes=['status'])
		三行代码，完成了失败订单列表。
	3、新需求：餐馆失败订单列表，减少了餐馆id这一列，并多了一些统计信息。
		减少列，重写get_line即可，不累述。
		统计信息是表级处理，重写get_rows_data，在这个方法中获得这些统计信息，附加在self上，之后输出。
	(前端直接处理额外讨论，我只是举个例子)

代码复用示例：
	1、构造最通用内容最详实的列表管理器OrderListManager，提供了订单列表的数据。
	2、新需求：失败订单列表，减少了状态status 成功/失败 这一列，要求不提供这样一列数据。
	    这时你可以这样做：
		用类FailedOrderListManager继承OrderListManager，重写get_line方法，excludes为[status]即可。如下：
		class FailedOrderListManager(OrderListManager):
			def get_line(self):
				return OrderListManager.get_line(self, exludes=['status'])
		三行代码，完成了失败订单列表。
	3、新需求：餐馆失败订单列表，减少了餐馆id这一列，并多了一些统计信息。
		减少列，重写get_line即可，不累述。
		统计信息是表级处理，重写get_rows_data，在这个方法中获得这些统计信息，附加在self上，之后输出。
	(前端直接处理额外讨论，我只是举个例子)
	
2、Widget 控件：ListManager的输出
	默认输出控件为Table。
	即使只是表格，所需格式也非常多样，需要你写自己的Table，来对应前端要求的格式。
	ListManager控制数据提取，Widget控制数据输出。

3、Form
	QForm 增加了 page/page_size/order_by用于处理分页/排序问题，无需重复写。

4、autodoc 高级帮助文档：
	基于django1.4版的admindocs，对views方法进行更细致的分析，不仅仅是显示注释。
	高度结构规范化的代码极为通俗易懂，不仅仅是人易于理解，机器同样易于理解。这使得我们编写一段代码来“读懂”另一段代码成为了可能。于是用一段框架代码去“读懂”你的代码，然后编写注释。
	当前对views方法的新注释包括：
	url、原注释、输入分析（Form表单）、核心数据（ListManager容器）。
	
5、autotest 自动测试：
	框架代码“读懂”了你的代码，自动产生测试去进行测试，不需要你自己写测试用例即可进行测试。
	测试模拟用户，产生请求、参数发送到运行中的网站，然后分析结果。对于需要“登录”的网站，你需要提供cookie填写在配置文件中，以表明这是某个登录用户。