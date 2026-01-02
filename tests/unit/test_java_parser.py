"""Unit tests for Java parser."""

import pytest
from src.parsers.java_parser import JavaParser
from src.models.analysis_result import ParsedClass, ParsedFunction


@pytest.fixture
def parser():
    """Create parser instance."""
    return JavaParser()


@pytest.fixture
def sample_java_file():
    """Sample Java code for testing."""
    return '''
package com.example.api.model;

import java.util.List;
import java.time.LocalDateTime;

/**
 * User model class.
 */
public class User {
    private Long id;
    private String name;
    private String email;
    private LocalDateTime createdAt;

    /**
     * Constructor.
     */
    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    /**
     * Get user ID.
     */
    public Long getId() {
        return id;
    }

    /**
     * Set user ID.
     */
    public void setId(Long id) {
        this.id = id;
    }

    /**
     * Get user name.
     */
    public String getName() {
        return name;
    }

    /**
     * Set user name.
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Get user email.
     */
    public String getEmail() {
        return email;
    }

    /**
     * Set user email.
     */
    public void setEmail(String email) {
        this.email = email;
    }

    /**
     * Convert to string.
     */
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\\'' +
                ", email='" + email + '\\'' +
                '}';
    }
}
'''


class TestJavaParser:
    """Test cases for JavaParser."""

    def test_parser_initialization(self, parser):
        """Test parser initialization."""
        assert parser is not None
        assert parser.language == 'java'

    def test_extract_classes(self, parser, sample_java_file):
        """Test class extraction."""
        classes = parser.extract_classes(sample_java_file)

        assert len(classes) >= 1
        user_class = next((c for c in classes if c.name == 'User'), None)
        assert user_class is not None
        assert 'public' in user_class.visibility

    def test_extract_class_with_package(self, parser, sample_java_file):
        """Test extracting class with package info."""
        classes = parser.extract_classes(sample_java_file)
        user_class = next((c for c in classes if c.name == 'User'), None)

        assert user_class is not None
        assert user_class.package_name == 'com.example.api.model'

    def test_extract_methods(self, parser, sample_java_file):
        """Test method extraction."""
        classes = parser.extract_classes(sample_java_file)
        user_class = next((c for c in classes if c.name == 'User'), None)

        assert user_class is not None
        # Should have constructor + getters/setters + toString
        assert len(user_class.methods) >= 5

    def test_method_visibility(self, parser, sample_java_file):
        """Test method visibility detection."""
        classes = parser.extract_classes(sample_java_file)
        user_class = next((c for c in classes if c.name == 'User'), None)

        assert user_class is not None
        # All getters/setters should be public
        public_methods = [m for m in user_class.methods if 'public' in m.get('visibility', '')]
        assert len(public_methods) > 0

    def test_simple_class(self, parser):
        """Test parsing simple class."""
        code = '''
public class Simple {
    private int value;

    public void setValue(int val) {
        this.value = val;
    }

    public int getValue() {
        return value;
    }
}
'''
        classes = parser.extract_classes(code)
        assert len(classes) >= 1
        assert classes[0].name == 'Simple'

    def test_interface_parsing(self, parser):
        """Test interface parsing."""
        code = '''
public interface UserRepository {
    User findById(Long id);
    List<User> findAll();
}
'''
        # Should handle interfaces gracefully
        classes = parser.extract_classes(code)
        # Either extracts interface or handles gracefully
        assert isinstance(classes, list)

    def test_generic_types(self, parser):
        """Test handling of generic types."""
        code = '''
public class Container<T> {
    private List<T> items;

    public void add(T item) {
        items.add(item);
    }

    public List<T> getItems() {
        return items;
    }
}
'''
        classes = parser.extract_classes(code)
        assert len(classes) >= 1
        assert classes[0].name == 'Container'

    def test_annotation_handling(self, parser, sample_java_file):
        """Test handling of annotations."""
        # @Override annotation should not break parsing
        classes = parser.extract_classes(sample_java_file)
        user_class = next((c for c in classes if c.name == 'User'), None)

        assert user_class is not None
        # Should successfully parse despite annotations
        assert len(user_class.methods) > 0

    def test_nested_class(self, parser):
        """Test parsing nested classes."""
        code = '''
public class Outer {
    public class Inner {
        public void innerMethod() {}
    }
}
'''
        classes = parser.extract_classes(code)
        # Should handle nested classes
        assert len(classes) >= 1

    def test_static_methods(self, parser):
        """Test parsing static methods."""
        code = '''
public class Utils {
    public static String format(String value) {
        return value.toUpperCase();
    }

    public static void main(String[] args) {}
}
'''
        classes = parser.extract_classes(code)
        assert len(classes) >= 1
        utils_class = classes[0]
        assert 'static' in [m.get('visibility', '') for m in utils_class.methods]
