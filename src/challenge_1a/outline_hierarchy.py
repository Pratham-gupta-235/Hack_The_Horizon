from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re

@dataclass
class OutlineNode:
    """Hierarchical outline node"""
    level: str
    text: str
    page: int
    parent_id: Optional[str] = None
    children: List['OutlineNode'] = field(default_factory=list)
    confidence: float = 0.0
    
    @property
    def level_number(self) -> int:
        """Get numeric level (1 for H1, 2 for H2, etc.)"""
        return int(self.level[1:]) if self.level.startswith('H') else 4

class OutlineHierarchy:
    """Build and manage hierarchical outline structure"""
    
    def __init__(self, config):
        self.config = config
        self._numbering_patterns = {}
        self._section_tracking = {}
    
    def build_hierarchy(self, headings: List[Dict[str, Any]]) -> List[OutlineNode]:
        """Build proper hierarchical structure from flat list"""
        if not headings:
            return []
        
        # Convert to nodes
        nodes = [self._create_node(heading) for heading in headings]
        
        # Analyze numbering patterns
        self._analyze_numbering_patterns(nodes)
        
        # Adjust levels based on patterns and context
        adjusted_nodes = self._adjust_hierarchy_levels(nodes)
        
        # Build parent-child relationships
        structured_nodes = self._build_parent_child_relationships(adjusted_nodes)
        
        return structured_nodes
    
    def _create_node(self, heading: Dict[str, Any]) -> OutlineNode:
        """Create outline node from heading data"""
        return OutlineNode(
            level=heading['level'],
            text=heading['text'],
            page=heading['page'],
            confidence=heading.get('confidence', 0.0)
        )
    
    def _analyze_numbering_patterns(self, nodes: List[OutlineNode]):
        """Analyze numbering patterns to improve hierarchy"""
        numbering_pattern = re.compile(r'^(\d+(?:\.\d+)*)')
        
        for node in nodes:
            match = numbering_pattern.match(node.text)
            if match:
                number_str = match.group(1)
                depth = number_str.count('.') + 1
                self._numbering_patterns[node.text] = depth
    
    def _adjust_hierarchy_levels(self, nodes: List[OutlineNode]) -> List[OutlineNode]:
        """Adjust hierarchy levels based on patterns and context"""
        adjusted_nodes = []
        level_stack = []
        
        for i, node in enumerate(nodes):
            # Check for numbering-based level
            if node.text in self._numbering_patterns:
                depth = self._numbering_patterns[node.text]
                node.level = f"H{min(depth, self.config.max_outline_depth)}"
            
            # Context-based adjustments
            if i > 0:
                prev_node = nodes[i-1]
                node = self._adjust_based_on_context(node, prev_node, level_stack)
            
            # Update level stack
            self._update_level_stack(level_stack, node)
            adjusted_nodes.append(node)
        
        return adjusted_nodes
    
    def _adjust_based_on_context(self, node: OutlineNode, prev_node: OutlineNode, 
                                level_stack: List[OutlineNode]) -> OutlineNode:
        """Adjust node level based on context"""
        # If same page and similar text, might be continuation
        if (node.page == prev_node.page and 
            self._are_similar_headings(node.text, prev_node.text)):
            node.level = prev_node.level
        
        # If much smaller font but high confidence, might be subheading
        elif (node.confidence >= 0.8 and 
              node.level_number > prev_node.level_number + 1):
            node.level = f"H{prev_node.level_number + 1}"
        
        return node
    
    def _are_similar_headings(self, text1: str, text2: str) -> bool:
        """Check if two headings are similar in structure"""
        # Simple similarity check based on common words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) > 0.3
    
    def _update_level_stack(self, level_stack: List[OutlineNode], node: OutlineNode):
        """Update the level stack for hierarchy tracking"""
        current_level = node.level_number
        
        # Remove levels deeper than current
        while level_stack and level_stack[-1].level_number >= current_level:
            level_stack.pop()
        
        level_stack.append(node)
    
    def _build_parent_child_relationships(self, nodes: List[OutlineNode]) -> List[OutlineNode]:
        """Build parent-child relationships"""
        if not nodes:
            return []
        
        root_nodes = []
        stack = []
        
        for node in nodes:
            current_level = node.level_number
            
            # Find appropriate parent
            while stack and stack[-1].level_number >= current_level:
                stack.pop()
            
            if stack:
                # Set parent
                parent = stack[-1]
                node.parent_id = f"{parent.page}_{hash(parent.text)}"
                parent.children.append(node)
            else:
                # Root node
                root_nodes.append(node)
            
            stack.append(node)
        
        return root_nodes
    
    def flatten_hierarchy(self, nodes: List[OutlineNode]) -> List[Dict[str, Any]]:
        """Flatten hierarchical structure back to list format"""
        flattened = []
        
        def _flatten_recursive(node_list: List[OutlineNode]):
            for node in node_list:
                flattened.append({
                    'level': node.level,
                    'text': node.text,
                    'page': node.page,
                    'parent_id': node.parent_id,
                    'confidence': node.confidence
                })
                if node.children:
                    _flatten_recursive(node.children)
        
        _flatten_recursive(nodes)
        return flattened
