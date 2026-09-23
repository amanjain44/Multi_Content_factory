from typing import Dict, Any, List
from ..graphs.demo_graph import build_demo_graph
from ..graphs.content_selection_graph import build_content_selection_graph
from ..graphs.platform_strategy_graph import build_platform_strategy_graph
from ..graphs.topic_angle_graph import build_topic_angle_graph
from ..graphs.content_strategy_graph import build_content_strategy_graph
from ..graphs.storyboard_graph import build_storyboard_graph
from ..graphs.script_graph import build_script_graph

class AIOrchestrator:
    def __init__(self):
        self.demo_graph = build_demo_graph()
        self.content_selection_graph = build_content_selection_graph()
        self.platform_strategy_graph = build_platform_strategy_graph()
        self.topic_angle_graph = build_topic_angle_graph()
        self.content_strategy_graph = build_content_strategy_graph()
        self.storyboard_graph = build_storyboard_graph()
        self.script_graph = build_script_graph()

    async def run_content_plan(self, input_text: str, grounding_context: dict | None = None) -> Dict[str, Any]:
        """
        Executes the demo graph to generate a content plan.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": None,
            "selected_platforms": None,
            "selected_angle": None,
            "approved_strategy": None,
            "approved_storyboard": None,
            "grounding_context": grounding_context or {},
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }
        
        try:
            # The ainvoke method handles the entire graph execution
            final_state = await self.demo_graph.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")
                
            return final_state.get("structured_output", {})
        except Exception as e:
            # Fallback handling
            raise RuntimeError(f"AI Orchestration Error: {str(e)}")

    async def run_content_selection(self, input_text: str, grounding_context: dict | None = None) -> Dict[str, Any]:
        """
        Executes the content selection graph to generate content opportunities.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": None,
            "selected_platforms": None,
            "selected_angle": None,
            "approved_strategy": None,
            "approved_storyboard": None,
            "grounding_context": grounding_context or {},
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }
        
        try:
            final_state = await self.content_selection_graph.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")
                
            return final_state.get("structured_output", {})
        except Exception as e:
            raise RuntimeError(f"Content Selection AI Error: {str(e)}")
            
    async def run_platform_strategy(self, input_text: str, selected_opportunity: dict, grounding_context: dict | None = None) -> Dict[str, Any]:
        """
        Executes the platform strategy graph to generate platform recommendations.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": selected_opportunity,
            "selected_platforms": None,
            "selected_angle": None,
            "approved_strategy": None,
            "approved_storyboard": None,
            "grounding_context": grounding_context or {},
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }
        
        try:
            final_state = await self.platform_strategy_graph.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")
                
            return final_state.get("structured_output", {})
        except Exception as e:
            raise RuntimeError(f"Platform Strategy AI Error: {str(e)}")

    async def run_topic_angle(self, input_text: str, selected_opportunity: dict, selected_platforms: List[dict], grounding_context: dict | None = None) -> Dict[str, Any]:
        """
        Executes the topic angle graph to generate content angles.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": selected_opportunity,
            "selected_platforms": selected_platforms,
            "selected_angle": None,
            "approved_strategy": None,
            "approved_storyboard": None,
            "grounding_context": grounding_context or {},
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }
        
        try:
            final_state = await self.topic_angle_graph.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")
                
            return final_state.get("structured_output", {})
        except Exception as e:
            raise RuntimeError(f"Topic Angle AI Error: {str(e)}")

    async def run_content_strategy(self, input_text: str, selected_opportunity: dict, selected_platforms: List[dict], selected_angle: dict, grounding_context: dict | None = None) -> Dict[str, Any]:
        """
        Executes the content strategy graph to generate a full strategy.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": selected_opportunity,
            "selected_platforms": selected_platforms,
            "selected_angle": selected_angle,
            "approved_strategy": None,
            "approved_storyboard": None,
            "grounding_context": grounding_context or {},
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }
        
        try:
            final_state = await self.content_strategy_graph.ainvoke(initial_state)
            
            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")
                
            return final_state.get("structured_output", {})
        except Exception as e:
            raise RuntimeError(f"Content Strategy AI Error: {str(e)}")

    async def run_storyboard(self, input_text: str, selected_opportunity: dict, selected_platforms: List[dict], selected_angle: dict, approved_strategy: dict, grounding_context: dict | None = None) -> Dict[str, Any]:
        """
        Executes the storyboard graph to generate scenes.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": selected_opportunity,
            "selected_platforms": selected_platforms,
            "selected_angle": selected_angle,
            "approved_strategy": approved_strategy,
            "approved_storyboard": None,
            "grounding_context": grounding_context or {},
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }
        
        try:
            final_state = await self.storyboard_graph.ainvoke(initial_state)

            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")

            return final_state.get("structured_output", {})
        except Exception as e:
            raise RuntimeError(f"Storyboard AI Error: {str(e)}")

    async def run_script(
        self,
        input_text: str,
        selected_opportunity: dict,
        selected_platforms: List[dict],
        selected_angle: dict,
        approved_strategy: dict,
        approved_storyboard: dict,
        grounding_context: dict | None = None
    ) -> Dict[str, Any]:
        """
        Executes the script graph to generate a final, publish-ready script
        by expanding each approved storyboard scene into a full script section.
        """
        initial_state = {
            "input_text": input_text,
            "selected_opportunity": selected_opportunity,
            "selected_platforms": selected_platforms,
            "selected_angle": selected_angle,
            "approved_strategy": approved_strategy,
            "approved_storyboard": approved_storyboard,
            "grounding_context": grounding_context,
            "intent": None,
            "keywords": None,
            "structured_output": None,
            "error": None,
            "retries": 0
        }

        try:
            final_state = await self.script_graph.ainvoke(initial_state)

            if final_state.get("error"):
                raise ValueError(f"Graph execution failed: {final_state['error']}")

            return final_state.get("structured_output", {})
        except Exception as e:
            raise RuntimeError(f"Script AI Error: {str(e)}")
