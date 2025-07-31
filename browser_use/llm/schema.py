"""Schema optimization utilities for LLM structured output."""

from typing import Any, Type

from pydantic import BaseModel


class SchemaOptimizer:
    """Optimizes Pydantic model schemas for LLM structured output."""
    
    @staticmethod
    def create_optimized_json_schema(model: Type[BaseModel]) -> dict[str, Any]:
        """
        Create an optimized JSON schema from a Pydantic model.
        
        Args:
            model: The Pydantic model class to create schema for
            
        Returns:
            The optimized JSON schema as a dictionary
        """
        # Get the base schema from the Pydantic model
        schema = model.model_json_schema()
        
        # Apply optimizations for LLM consumption
        optimized_schema = SchemaOptimizer._optimize_schema(schema)
        
        return optimized_schema
    
    @staticmethod
    def _optimize_schema(schema: dict[str, Any]) -> dict[str, Any]:
        """
        Apply optimizations to the schema for better LLM performance.
        
        Args:
            schema: The original JSON schema
            
        Returns:
            The optimized schema
        """
        # Create a copy to avoid modifying the original
        optimized = schema.copy()
        
        # Remove unnecessary fields that can confuse LLMs
        if '$defs' in optimized:
            # Clean up $defs section
            optimized['$defs'] = SchemaOptimizer._clean_defs(optimized['$defs'])
        
        # Ensure all required fields are properly marked
        if 'required' not in optimized and 'properties' in optimized:
            # Mark all properties as required by default for stricter validation
            optimized['required'] = list(optimized['properties'].keys())
        
        return optimized
    
    @staticmethod
    def _clean_defs(defs: dict[str, Any]) -> dict[str, Any]:
        """
        Clean up the $defs section of the schema.
        
        Args:
            defs: The $defs dictionary from the schema
            
        Returns:
            Cleaned $defs dictionary
        """
        cleaned_defs = {}
        
        for key, value in defs.items():
            if isinstance(value, dict):
                # Keep the definition but clean it up
                cleaned_value = value.copy()
                
                # Remove redundant fields that LLMs don't need
                fields_to_remove = ['title', 'description'] if 'properties' in cleaned_value else []
                for field in fields_to_remove:
                    cleaned_value.pop(field, None)
                
                cleaned_defs[key] = cleaned_value
            else:
                cleaned_defs[key] = value
        
        return cleaned_defs
