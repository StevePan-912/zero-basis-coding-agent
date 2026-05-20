# backend/tests/test_teaching_content_db.py
"""
Tests for TeachingContentDatabase class.
"""

import pytest
from app.database import TeachingContentDatabase, TeachingContent


class TestTeachingContentDatabase:
    """Tests for TeachingContentDatabase class."""

    def test_init_default_content(self):
        """Test that database initializes with default content."""
        db = TeachingContentDatabase()

        # Should have 6 default concepts
        concepts = db.get_all_concepts()
        assert len(concepts) == 6

        # Should have all required concepts
        expected_concepts = {'变量', '函数', '循环', '条件判断', '列表', '字典'}
        assert set(concepts) == expected_concepts

    def test_init_has_beginner_content(self):
        """Test that database has beginner level content."""
        db = TeachingContentDatabase()

        beginner_content = db.get_content_by_difficulty('beginner')
        assert len(beginner_content) == 4

        # Verify concept names
        beginner_concepts = {c['concept_name'] for c in beginner_content}
        assert beginner_concepts == {'变量', '函数', '循环', '条件判断'}

    def test_init_has_intermediate_content(self):
        """Test that database has intermediate level content."""
        db = TeachingContentDatabase()

        intermediate_content = db.get_content_by_difficulty('intermediate')
        assert len(intermediate_content) == 2

        # Verify concept names
        intermediate_concepts = {c['concept_name'] for c in intermediate_content}
        assert intermediate_concepts == {'列表', '字典'}

    def test_get_content_by_concept_exists(self):
        """Test getting content by concept name that exists."""
        db = TeachingContentDatabase()

        content = db.get_content_by_concept('变量')
        assert content is not None
        assert content['concept_name'] == '变量'
        assert content['difficulty_level'] == 'beginner'
        assert '变量是存储数据的容器' in content['explanation']
        assert len(content['analogies']) > 0
        assert len(content['code_examples']) > 0
        assert len(content['related_concepts']) > 0

    def test_get_content_by_concept_not_exists(self):
        """Test getting content by concept name that does not exist."""
        db = TeachingContentDatabase()

        content = db.get_content_by_concept('不存在的概念')
        assert content is None

    def test_get_content_by_difficulty_beginner(self):
        """Test getting content by beginner difficulty."""
        db = TeachingContentDatabase()

        content = db.get_content_by_difficulty('beginner')
        assert len(content) == 4
        assert all(c['difficulty_level'] == 'beginner' for c in content)

    def test_get_content_by_difficulty_intermediate(self):
        """Test getting content by intermediate difficulty."""
        db = TeachingContentDatabase()

        content = db.get_content_by_difficulty('intermediate')
        assert len(content) == 2
        assert all(c['difficulty_level'] == 'intermediate' for c in content)

    def test_get_content_by_difficulty_advanced_empty(self):
        """Test getting content by advanced difficulty (should be empty)."""
        db = TeachingContentDatabase()

        content = db.get_content_by_difficulty('advanced')
        assert len(content) == 0

    def test_get_content_by_difficulty_invalid(self):
        """Test that invalid difficulty raises ValueError."""
        db = TeachingContentDatabase()

        with pytest.raises(ValueError, match="Invalid difficulty"):
            db.get_content_by_difficulty('invalid')

    def test_search_content_by_concept_name(self):
        """Test searching content by concept name keyword."""
        db = TeachingContentDatabase()

        # Search for '变量'
        results = db.search_content('变量')
        assert len(results) == 1
        assert results[0]['concept_name'] == '变量'

    def test_search_content_by_explanation(self):
        """Test searching content by explanation keyword."""
        db = TeachingContentDatabase()

        # Search for '容器'
        results = db.search_content('容器')
        assert len(results) >= 1

        # Should find '变量' which mentions '容器' in explanation
        concept_names = {r['concept_name'] for r in results}
        assert '变量' in concept_names

    def test_search_content_by_analogy(self):
        """Test searching content by analogy keyword."""
        db = TeachingContentDatabase()

        # Search for '盒子'
        results = db.search_content('盒子')
        assert len(results) >= 1

        # Should find '变量' which has analogy about '盒子'
        concept_names = {r['concept_name'] for r in results}
        assert '变量' in concept_names

    def test_search_content_no_match(self):
        """Test searching with keyword that has no match."""
        db = TeachingContentDatabase()

        results = db.search_content('xyzabc123不存在的关键词')
        assert len(results) == 0

    def test_search_content_empty_keyword(self):
        """Test searching with empty keyword."""
        db = TeachingContentDatabase()

        results = db.search_content('')
        assert len(results) == 0

    def test_search_content_case_insensitive(self):
        """Test that search is case insensitive."""
        db = TeachingContentDatabase()

        # Chinese characters don't have case, but test with mixed input
        results1 = db.search_content('函数')
        results2 = db.search_content('FUNCTION')  # English keyword

        # At least '函数' should be found
        assert len(results1) >= 1

    def test_add_custom_content(self):
        """Test adding custom content."""
        db = TeachingContentDatabase()

        initial_count = db.count_content()

        content_id = db.add_custom_content({
            'concept_name': '类',
            'difficulty_level': 'intermediate',
            'explanation': '类是面向对象编程的核心概念，用于创建对象。',
            'analogies': ['类就像蓝图，对象是根据蓝图建造的房子'],
            'code_examples': [{'language': 'python', 'code': 'class Dog:', 'description': '定义类'}],
            'related_concepts': ['对象', '继承', '封装']
        })

        assert db.count_content() == initial_count + 1

        # Verify content was added
        content = db.get_content_by_id(content_id)
        assert content is not None
        assert content['concept_name'] == '类'
        assert content['difficulty_level'] == 'intermediate'
        assert len(content['analogies']) == 1
        assert len(content['related_concepts']) == 3

    def test_add_custom_content_minimal(self):
        """Test adding custom content with only required fields."""
        db = TeachingContentDatabase()

        content_id = db.add_custom_content({
            'concept_name': '异常处理',
            'difficulty_level': 'beginner',
            'explanation': '异常处理用于处理程序运行时的错误。'
        })

        content = db.get_content_by_id(content_id)
        assert content is not None
        assert content['concept_name'] == '异常处理'
        assert content['analogies'] == []
        assert content['code_examples'] == []
        assert content['visual_diagrams'] == []
        assert content['related_concepts'] == []

    def test_add_custom_content_missing_concept_name(self):
        """Test that adding content without concept_name raises ValueError."""
        db = TeachingContentDatabase()

        with pytest.raises(ValueError, match="Missing required fields"):
            db.add_custom_content({
                'difficulty_level': 'beginner',
                'explanation': 'Test explanation'
            })

    def test_add_custom_content_missing_difficulty_level(self):
        """Test that adding content without difficulty_level raises ValueError."""
        db = TeachingContentDatabase()

        with pytest.raises(ValueError, match="Missing required fields"):
            db.add_custom_content({
                'concept_name': '测试概念',
                'explanation': 'Test explanation'
            })

    def test_add_custom_content_missing_explanation(self):
        """Test that adding content without explanation raises ValueError."""
        db = TeachingContentDatabase()

        with pytest.raises(ValueError, match="Missing required fields"):
            db.add_custom_content({
                'concept_name': '测试概念',
                'difficulty_level': 'beginner'
            })

    def test_add_custom_content_invalid_difficulty(self):
        """Test that adding content with invalid difficulty raises ValueError."""
        db = TeachingContentDatabase()

        with pytest.raises(ValueError, match="Invalid difficulty_level"):
            db.add_custom_content({
                'concept_name': '测试概念',
                'difficulty_level': 'expert',
                'explanation': 'Test explanation'
            })

    def test_add_custom_content_duplicate_concept_name(self):
        """Test that adding content with duplicate concept_name raises ValueError."""
        db = TeachingContentDatabase()

        with pytest.raises(ValueError, match="already exists"):
            db.add_custom_content({
                'concept_name': '变量',  # This already exists
                'difficulty_level': 'beginner',
                'explanation': 'Another explanation'
            })

    def test_get_all_concepts(self):
        """Test getting all concept names."""
        db = TeachingContentDatabase()

        concepts = db.get_all_concepts()

        assert len(concepts) == 6
        assert '变量' in concepts
        assert '函数' in concepts
        assert '循环' in concepts
        assert '条件判断' in concepts
        assert '列表' in concepts
        assert '字典' in concepts

    def test_get_content_by_id_exists(self):
        """Test getting content by ID that exists."""
        db = TeachingContentDatabase()

        # First get a concept to find its ID
        content = db.get_content_by_concept('变量')
        content_id = content['id']

        # Now get by ID
        retrieved = db.get_content_by_id(content_id)
        assert retrieved is not None
        assert retrieved['concept_name'] == '变量'

    def test_get_content_by_id_not_exists(self):
        """Test getting content by ID that does not exist."""
        db = TeachingContentDatabase()

        content = db.get_content_by_id('non-existent-id-12345')
        assert content is None

    def test_get_all_content(self):
        """Test getting all content."""
        db = TeachingContentDatabase()

        all_content = db.get_all_content()

        assert len(all_content) == 6
        assert all('concept_name' in c for c in all_content)
        assert all('difficulty_level' in c for c in all_content)
        assert all('explanation' in c for c in all_content)

    def test_delete_content(self):
        """Test deleting content."""
        db = TeachingContentDatabase()

        # Add custom content to delete
        content_id = db.add_custom_content({
            'concept_name': '待删除概念',
            'difficulty_level': 'beginner',
            'explanation': '这个概念将被删除'
        })

        initial_count = db.count_content()

        # Delete the content
        result = db.delete_content(content_id)
        assert result is True
        assert db.count_content() == initial_count - 1

        # Verify content is gone
        content = db.get_content_by_id(content_id)
        assert content is None

    def test_delete_content_not_exists(self):
        """Test deleting content that does not exist."""
        db = TeachingContentDatabase()

        result = db.delete_content('non-existent-id-12345')
        assert result is False

    def test_count_content(self):
        """Test counting content."""
        db = TeachingContentDatabase()

        count = db.count_content()
        assert count == 6

        # Add content
        db.add_custom_content({
            'concept_name': '新概念',
            'difficulty_level': 'beginner',
            'explanation': '新概念的解释'
        })

        assert db.count_content() == 7

    def test_content_has_analogies(self):
        """Test that each default content has analogies."""
        db = TeachingContentDatabase()

        for concept in db.get_all_concepts():
            content = db.get_content_by_concept(concept)
            assert content is not None
            assert len(content['analogies']) > 0, f"{concept} should have analogies"

    def test_content_has_code_examples(self):
        """Test that each default content has code examples."""
        db = TeachingContentDatabase()

        for concept in db.get_all_concepts():
            content = db.get_content_by_concept(concept)
            assert content is not None
            assert len(content['code_examples']) > 0, f"{concept} should have code examples"

    def test_content_has_related_concepts(self):
        """Test that each default content has related concepts."""
        db = TeachingContentDatabase()

        for concept in db.get_all_concepts():
            content = db.get_content_by_concept(concept)
            assert content is not None
            assert len(content['related_concepts']) > 0, f"{concept} should have related concepts"


class TestTeachingContent:
    """Tests for TeachingContent model."""

    def test_teaching_content_creation(self):
        """Test creating a TeachingContent instance."""
        from datetime import datetime

        content = TeachingContent(
            id='test-id',
            concept_name='测试概念',
            difficulty_level='beginner',
            explanation='这是测试解释',
            analogies=['类比1', '类比2'],
            code_examples=[{'language': 'python', 'code': 'print("hello")'}],
            visual_diagrams=[{'type': 'box', 'description': 'test'}],
            related_concepts=['概念A', '概念B']
        )

        assert content.id == 'test-id'
        assert content.concept_name == '测试概念'
        assert content.difficulty_level == 'beginner'
        assert content.explanation == '这是测试解释'
        assert len(content.analogies) == 2
        assert len(content.code_examples) == 1
        assert len(content.visual_diagrams) == 1
        assert len(content.related_concepts) == 2

    def test_teaching_content_to_dict(self):
        """Test converting TeachingContent to dictionary."""
        content = TeachingContent(
            id='test-id',
            concept_name='测试概念',
            difficulty_level='beginner',
            explanation='这是测试解释',
            analogies=['类比1'],
            code_examples=[],
            visual_diagrams=[],
            related_concepts=['概念A']
        )

        data = content.to_dict()

        assert data['id'] == 'test-id'
        assert data['concept_name'] == '测试概念'
        assert data['difficulty_level'] == 'beginner'
        assert data['explanation'] == '这是测试解释'
        assert data['analogies'] == ['类比1']
        assert 'created_at' in data

    def test_teaching_content_from_dict(self):
        """Test creating TeachingContent from dictionary."""
        data = {
            'id': 'test-id',
            'concept_name': '测试概念',
            'difficulty_level': 'beginner',
            'explanation': '这是测试解释',
            'analogies': ['类比1', '类比2'],
            'code_examples': [{'language': 'python', 'code': 'test'}],
            'visual_diagrams': [],
            'related_concepts': ['概念A']
        }

        content = TeachingContent.from_dict(data)

        assert content.id == 'test-id'
        assert content.concept_name == '测试概念'
        assert content.difficulty_level == 'beginner'
        assert content.explanation == '这是测试解释'
        assert len(content.analogies) == 2
        assert len(content.code_examples) == 1

    def test_teaching_content_from_dict_with_iso_datetime(self):
        """Test creating TeachingContent with ISO format datetime string."""
        from datetime import datetime

        now = datetime.now()
        iso_string = now.isoformat()

        data = {
            'id': 'test-id',
            'concept_name': '测试概念',
            'difficulty_level': 'beginner',
            'explanation': '这是测试解释',
            'created_at': iso_string
        }

        content = TeachingContent.from_dict(data)

        assert content.created_at is not None
        assert isinstance(content.created_at, datetime)

    def test_teaching_content_roundtrip(self):
        """Test converting to dict and back preserves data."""
        original = TeachingContent(
            id='test-id',
            concept_name='测试概念',
            difficulty_level='intermediate',
            explanation='这是测试解释',
            analogies=['类比1', '类比2'],
            code_examples=[{'language': 'python', 'code': 'print("hello")'}],
            visual_diagrams=[{'type': 'box', 'description': 'test'}],
            related_concepts=['概念A', '概念B']
        )

        data = original.to_dict()
        restored = TeachingContent.from_dict(data)

        assert restored.id == original.id
        assert restored.concept_name == original.concept_name
        assert restored.difficulty_level == original.difficulty_level
        assert restored.explanation == original.explanation
        assert restored.analogies == original.analogies
        assert restored.code_examples == original.code_examples
        assert restored.visual_diagrams == original.visual_diagrams
        assert restored.related_concepts == original.related_concepts


class TestTeachingContentDatabaseEdgeCases:
    """Edge case tests for TeachingContentDatabase."""

    def test_search_content_partial_match(self):
        """Test searching with partial keyword match."""
        db = TeachingContentDatabase()

        # Search for partial match
        results = db.search_content('变')
        assert len(results) >= 1

        # Should find '变量'
        concept_names = {r['concept_name'] for r in results}
        assert '变量' in concept_names

    def test_multiple_searches_independent(self):
        """Test that multiple searches are independent."""
        db = TeachingContentDatabase()

        results1 = db.search_content('变量')
        results2 = db.search_content('函数')

        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0]['concept_name'] == '变量'
        assert results2[0]['concept_name'] == '函数'

    def test_database_instances_independent(self):
        """Test that different database instances are independent."""
        db1 = TeachingContentDatabase()
        db2 = TeachingContentDatabase()

        # Add content to db1
        db1.add_custom_content({
            'concept_name': 'DB1概念',
            'difficulty_level': 'beginner',
            'explanation': 'DB1解释'
        })

        # db2 should not have the new content
        assert db1.get_content_by_concept('DB1概念') is not None
        assert db2.get_content_by_concept('DB1概念') is None

    def test_add_content_with_id(self):
        """Test adding content with custom ID."""
        db = TeachingContentDatabase()

        custom_id = 'custom-id-12345'
        content_id = db.add_custom_content({
            'id': custom_id,
            'concept_name': '自定义ID概念',
            'difficulty_level': 'beginner',
            'explanation': '带自定义ID的概念'
        })

        assert content_id == custom_id
        content = db.get_content_by_id(custom_id)
        assert content is not None
        assert content['concept_name'] == '自定义ID概念'

    def test_content_structure_integrity(self):
        """Test that content structure is correct."""
        db = TeachingContentDatabase()

        content = db.get_content_by_concept('函数')

        # Check all required fields exist
        assert 'id' in content
        assert 'concept_name' in content
        assert 'difficulty_level' in content
        assert 'explanation' in content
        assert 'analogies' in content
        assert 'code_examples' in content
        assert 'visual_diagrams' in content
        assert 'related_concepts' in content
        assert 'created_at' in content

        # Check types
        assert isinstance(content['analogies'], list)
        assert isinstance(content['code_examples'], list)
        assert isinstance(content['visual_diagrams'], list)
        assert isinstance(content['related_concepts'], list)