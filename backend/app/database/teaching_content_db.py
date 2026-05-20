# backend/app/database/teaching_content_db.py
"""
TeachingContentDatabase - Manages teaching content for programming concepts.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.database.models import TeachingContent


class TeachingContentDatabase:
    """
    Manages teaching content for programming concepts.

    Provides methods to query, search, and add teaching content.
    """

    # Valid difficulty levels
    VALID_DIFFICULTIES = {'beginner', 'intermediate', 'advanced'}

    # Required fields for teaching content
    REQUIRED_FIELDS = {'id', 'concept_name', 'difficulty_level', 'explanation'}

    def __init__(self):
        """Initialize TeachingContentDatabase with default content."""
        self._content: Dict[str, TeachingContent] = {}
        self._concept_index: Dict[str, str] = {}  # concept_name -> id mapping
        self._init_default_content()

    def _init_default_content(self) -> None:
        """
        Initialize database with default teaching content.

        Creates 6 core programming concepts:
        - 变量 (beginner)
        - 函数 (beginner)
        - 循环 (beginner)
        - 条件判断 (beginner)
        - 列表 (intermediate)
        - 字典 (intermediate)
        """
        default_content = [
            {
                'id': str(uuid.uuid4()),
                'concept_name': '变量',
                'difficulty_level': 'beginner',
                'explanation': '变量是存储数据的容器。你可以把变量想象成一个带有标签的盒子，盒子用来存放数据，标签就是变量名，方便你找到和使用这些数据。',
                'analogies': [
                    '变量就像一个贴有标签的盒子，你可以往里面放东西，也可以随时更换里面的内容',
                    '变量就像手机里的通讯录，姓名是变量名，电话号码是存储的值',
                    '变量就像一杯水，杯子是变量名，水是存储的值，你可以随时把水换成其他饮料'
                ],
                'code_examples': [
                    {
                        'language': 'python',
                        'code': '# 创建变量\nname = "小明"\nage = 18\nheight = 1.75\n\nprint(name)  # 输出: 小明\nprint(age)   # 输出: 18',
                        'description': '创建和打印变量'
                    },
                    {
                        'language': 'python',
                        'code': '# 修改变量的值\nscore = 90\nprint(score)  # 输出: 90\n\nscore = 95\nprint(score)  # 输出: 95',
                        'description': '变量值可以被修改'
                    }
                ],
                'visual_diagrams': [
                    {
                        'type': 'box_diagram',
                        'description': '变量名 → [值]',
                        'svg': '<svg>...</svg>'
                    }
                ],
                'related_concepts': ['数据类型', '赋值', '常量']
            },
            {
                'id': str(uuid.uuid4()),
                'concept_name': '函数',
                'difficulty_level': 'beginner',
                'explanation': '函数是一段可重复使用的代码块，它封装了特定的功能。你可以把函数想象成一个"机器"，输入原料（参数），经过加工处理，产出产品（返回值）。',
                'analogies': [
                    '函数就像一台自动售货机，你投入硬币（参数），按下按钮，它就会吐出饮料（返回值）',
                    '函数就像洗衣机，你把脏衣服放进去（参数），按下开始按钮，它就会给你洗干净的衣服（返回值）',
                    '函数就像菜谱，按照步骤（函数体）就能做出一道菜，每次都能重复使用这个菜谱'
                ],
                'code_examples': [
                    {
                        'language': 'python',
                        'code': '# 定义一个简单的函数\ndef greet(name):\n    return f"你好, {name}!"\n\n# 调用函数\nmessage = greet("小明")\nprint(message)  # 输出: 你好, 小明!',
                        'description': '定义和调用函数'
                    },
                    {
                        'language': 'python',
                        'code': '# 有多个参数的函数\ndef calculate_area(length, width):\n    return length * width\n\narea = calculate_area(5, 3)\nprint(area)  # 输出: 15',
                        'description': '函数可以接受多个参数'
                    }
                ],
                'visual_diagrams': [
                    {
                        'type': 'flow_diagram',
                        'description': '输入 → [函数处理] → 输出',
                        'svg': '<svg>...</svg>'
                    }
                ],
                'related_concepts': ['参数', '返回值', '递归', '匿名函数']
            },
            {
                'id': str(uuid.uuid4()),
                'concept_name': '循环',
                'difficulty_level': 'beginner',
                'explanation': '循环是重复执行某段代码的结构。当你需要多次执行相同的操作时，不需要重复写代码，使用循环可以大大简化代码。',
                'analogies': [
                    '循环就像跑步，围着操场跑5圈，每圈都是同样的路线，但不需要每次都重新规划',
                    '循环就像做广播体操，每个动作重复做4次，按照指令重复执行',
                    '循环就像背乘法口诀，从"一一得一"到"九九八十一"，依次重复背诵'
                ],
                'code_examples': [
                    {
                        'language': 'python',
                        'code': '# for循环\nfor i in range(5):\n    print(f"第{i+1}次循环")\n# 输出:\n# 第1次循环\n# 第2次循环\n# 第3次循环\n# 第4次循环\n# 第5次循环',
                        'description': 'for循环示例'
                    },
                    {
                        'language': 'python',
                        'code': '# while循环\ncount = 0\nwhile count < 3:\n    print(f"count = {count}")\n    count += 1\n# 输出:\n# count = 0\n# count = 1\n# count = 2',
                        'description': 'while循环示例'
                    },
                    {
                        'language': 'python',
                        'code': '# 遍历列表\nfruits = ["苹果", "香蕉", "橙子"]\nfor fruit in fruits:\n    print(f"我喜欢吃{fruit}")',
                        'description': '遍历列表中的元素'
                    }
                ],
                'visual_diagrams': [
                    {
                        'type': 'flow_diagram',
                        'description': '开始 → 条件判断 → 执行代码 → 返回条件判断 → 结束',
                        'svg': '<svg>...</svg>'
                    }
                ],
                'related_concepts': ['for循环', 'while循环', 'break', 'continue', '嵌套循环']
            },
            {
                'id': str(uuid.uuid4()),
                'concept_name': '条件判断',
                'difficulty_level': 'beginner',
                'explanation': '条件判断是根据条件执行不同代码的逻辑。它就像生活中的"如果...那么..."，让程序能够根据不同的情况做出不同的反应。',
                'analogies': [
                    '条件判断就像交通信号灯：如果是红灯就停下来，如果是绿灯就走',
                    '条件判断就像点餐：如果想要辣的就加辣椒，如果不要辣的就不加',
                    '条件判断就像考试评分：如果分数大于等于90分就是优秀，如果分数大于等于60分就是及格，否则就是不及格'
                ],
                'code_examples': [
                    {
                        'language': 'python',
                        'code': '# if-else语句\nscore = 85\n\nif score >= 90:\n    print("优秀")\nelif score >= 60:\n    print("及格")\nelse:\n    print("不及格")\n# 输出: 及格',
                        'description': 'if-elif-else语句'
                    },
                    {
                        'language': 'python',
                        'code': '# 简单的if语句\nage = 18\n\nif age >= 18:\n    print("你已经成年了")\n# 输出: 你已经成年了',
                        'description': '简单的if语句'
                    },
                    {
                        'language': 'python',
                        'code': '# 嵌套条件判断\nhas_ticket = True\nage = 20\n\nif has_ticket:\n    if age >= 18:\n        print("欢迎进入")\n    else:\n        print("未成年人需要家长陪同")\nelse:\n    print("请先购买门票")',
                        'description': '嵌套的条件判断'
                    }
                ],
                'visual_diagrams': [
                    {
                        'type': 'flow_diagram',
                        'description': '条件判断 → 是 → 执行代码A → 否 → 执行代码B',
                        'svg': '<svg>...</svg>'
                    }
                ],
                'related_concepts': ['比较运算符', '逻辑运算符', '三元运算符', 'switch语句']
            },
            {
                'id': str(uuid.uuid4()),
                'concept_name': '列表',
                'difficulty_level': 'intermediate',
                'explanation': '列表是存储多个数据的有序集合。列表中的每个元素都有一个位置编号（索引），从0开始计数。列表可以存储不同类型的数据，并且可以随时添加或删除元素。',
                'analogies': [
                    '列表就像一排储物柜，每个柜子都有一个编号（索引），可以存放不同的物品',
                    '列表就像购物清单，按照顺序列出要买的东西，可以随时添加或划掉',
                    '列表就像火车车厢，每节车厢都有编号，可以装载不同的货物'
                ],
                'code_examples': [
                    {
                        'language': 'python',
                        'code': '# 创建和访问列表\nfruits = ["苹果", "香蕉", "橙子"]\nprint(fruits[0])  # 输出: 苹果\nprint(fruits[1])  # 输出: 香蕉\nprint(fruits[-1]) # 输出: 橙子 (最后一个元素)',
                        'description': '创建和访问列表元素'
                    },
                    {
                        'language': 'python',
                        'code': '# 修改列表\nnumbers = [1, 2, 3, 4, 5]\nnumbers.append(6)      # 添加元素\nnumbers.remove(3)     # 删除元素\nnumbers[0] = 0        # 修改元素\nprint(numbers)        # 输出: [0, 2, 4, 5, 6]',
                        'description': '列表的增删改操作'
                    },
                    {
                        'language': 'python',
                        'code': '# 列表切片\nnumbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]\nprint(numbers[2:5])   # 输出: [2, 3, 4]\nprint(numbers[:3])    # 输出: [0, 1, 2]\nprint(numbers[7:])    # 输出: [7, 8, 9]\nprint(numbers[::2])   # 输出: [0, 2, 4, 6, 8]',
                        'description': '列表切片操作'
                    }
                ],
                'visual_diagrams': [
                    {
                        'type': 'array_diagram',
                        'description': '[元素0, 元素1, 元素2, ...] 索引从0开始',
                        'svg': '<svg>...</svg>'
                    }
                ],
                'related_concepts': ['索引', '切片', '列表方法', '列表推导式', '元组']
            },
            {
                'id': str(uuid.uuid4()),
                'concept_name': '字典',
                'difficulty_level': 'intermediate',
                'explanation': '字典是存储键值对的无序集合。每个元素由一个键和对应的值组成，通过键可以快速找到对应的值。字典非常适合存储有关联关系的数据。',
                'analogies': [
                    '字典就像真实的字典，通过词语（键）查找解释（值）',
                    '字典就像电话簿，通过姓名（键）查找电话号码（值）',
                    '字典就像储物柜的钥匙，每把钥匙（键）对应一个柜子（值）'
                ],
                'code_examples': [
                    {
                        'language': 'python',
                        'code': '# 创建和访问字典\nstudent = {\n    "name": "小明",\n    "age": 18,\n    "grade": "高三"\n}\nprint(student["name"])   # 输出: 小明\nprint(student["age"])    # 输出: 18',
                        'description': '创建和访问字典'
                    },
                    {
                        'language': 'python',
                        'code': '# 修改字典\nstudent = {"name": "小明", "age": 18}\nstudent["age"] = 19          # 修改值\nstudent["gender"] = "男"     # 添加新键值对\ndel student["name"]          # 删除键值对\nprint(student)  # 输出: {\'age\': 19, \'gender\': \'男\'}',
                        'description': '字典的增删改操作'
                    },
                    {
                        'language': 'python',
                        'code': '# 遍历字典\nstudent = {"name": "小明", "age": 18, "grade": "高三"}\n\n# 遍历所有键\nfor key in student:\n    print(key)\n\n# 遍历所有键值对\nfor key, value in student.items():\n    print(f"{key}: {value}")',
                        'description': '遍历字典'
                    }
                ],
                'visual_diagrams': [
                    {
                        'type': 'key_value_diagram',
                        'description': '键 → 值，一一对应关系',
                        'svg': '<svg>...</svg>'
                    }
                ],
                'related_concepts': ['键值对', '字典方法', '嵌套字典', 'JSON', '集合']
            }
        ]

        for content_data in default_content:
            content = TeachingContent.from_dict(content_data)
            self._content[content.id] = content
            self._concept_index[content.concept_name] = content.id

    def get_content_by_concept(self, concept_name: str) -> Optional[Dict[str, Any]]:
        """
        Get teaching content by concept name.

        Args:
            concept_name: Name of the concept to search for.

        Returns:
            Dictionary representation of the teaching content, or None if not found.
        """
        content_id = self._concept_index.get(concept_name)
        if content_id:
            return self._content[content_id].to_dict()
        return None

    def get_content_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        Get all teaching content for a specific difficulty level.

        Args:
            difficulty: Difficulty level to filter by ('beginner', 'intermediate', 'advanced').

        Returns:
            List of teaching content dictionaries for the specified difficulty.

        Raises:
            ValueError: If difficulty is not a valid difficulty level.
        """
        if difficulty not in self.VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty '{difficulty}'. Must be one of: {self.VALID_DIFFICULTIES}"
            )

        return [
            content.to_dict()
            for content in self._content.values()
            if content.difficulty_level == difficulty
        ]

    def search_content(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search teaching content by keyword.

        Searches in concept_name, explanation, and analogies fields.

        Args:
            keyword: Keyword to search for.

        Returns:
            List of teaching content dictionaries matching the keyword.
        """
        if not keyword:
            return []

        keyword_lower = keyword.lower()
        results = []

        for content in self._content.values():
            # Search in concept_name
            if keyword_lower in content.concept_name.lower():
                results.append(content.to_dict())
                continue

            # Search in explanation
            if keyword_lower in content.explanation.lower():
                results.append(content.to_dict())
                continue

            # Search in analogies
            for analogy in content.analogies:
                if keyword_lower in analogy.lower():
                    results.append(content.to_dict())
                    break

        return results

    def add_custom_content(self, content: Dict[str, Any]) -> str:
        """
        Add custom teaching content to the database.

        Args:
            content: Dictionary containing teaching content data.
                Must include: concept_name, difficulty_level, explanation
                Optional: analogies, code_examples, visual_diagrams, related_concepts

        Returns:
            The ID of the newly added content.

        Raises:
            ValueError: If required fields are missing or invalid values.
        """
        # Validate required fields
        missing_fields = self.REQUIRED_FIELDS - set(content.keys())
        # Note: id is auto-generated, so we check for concept_name, difficulty_level, explanation
        required_user_fields = {'concept_name', 'difficulty_level', 'explanation'}
        missing_user_fields = required_user_fields - set(content.keys())

        if missing_user_fields:
            raise ValueError(
                f"Missing required fields: {missing_user_fields}. "
                f"Content must include: {required_user_fields}"
            )

        # Validate difficulty level
        if content['difficulty_level'] not in self.VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty_level '{content['difficulty_level']}'. "
                f"Must be one of: {self.VALID_DIFFICULTIES}"
            )

        # Check for duplicate concept name
        if content['concept_name'] in self._concept_index:
            raise ValueError(
                f"Content with concept_name '{content['concept_name']}' already exists"
            )

        # Generate ID and create content
        content_id = content.get('id', str(uuid.uuid4()))

        new_content = TeachingContent(
            id=content_id,
            concept_name=content['concept_name'],
            difficulty_level=content['difficulty_level'],
            explanation=content['explanation'],
            analogies=content.get('analogies', []),
            code_examples=content.get('code_examples', []),
            visual_diagrams=content.get('visual_diagrams', []),
            related_concepts=content.get('related_concepts', []),
            created_at=datetime.fromisoformat(content['created_at']) if isinstance(content.get('created_at'), str) else content.get('created_at', datetime.now())
        )

        self._content[content_id] = new_content
        self._concept_index[new_content.concept_name] = content_id

        return content_id

    def get_all_concepts(self) -> List[str]:
        """
        Get all concept names in the database.

        Returns:
            List of concept names.
        """
        return list(self._concept_index.keys())

    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get teaching content by ID.

        Args:
            content_id: ID of the content to retrieve.

        Returns:
            Dictionary representation of the teaching content, or None if not found.
        """
        content = self._content.get(content_id)
        if content:
            return content.to_dict()
        return None

    def get_all_content(self) -> List[Dict[str, Any]]:
        """
        Get all teaching content in the database.

        Returns:
            List of all teaching content dictionaries.
        """
        return [content.to_dict() for content in self._content.values()]

    def delete_content(self, content_id: str) -> bool:
        """
        Delete teaching content by ID.

        Args:
            content_id: ID of the content to delete.

        Returns:
            True if content was deleted, False if content was not found.
        """
        if content_id not in self._content:
            return False

        content = self._content[content_id]
        del self._concept_index[content.concept_name]
        del self._content[content_id]

        return True

    def count_content(self) -> int:
        """
        Count total number of teaching content items.

        Returns:
            Number of content items in the database.
        """
        return len(self._content)