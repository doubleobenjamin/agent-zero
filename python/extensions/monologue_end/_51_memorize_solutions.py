import asyncio
from python.helpers.extension import Extension
from python.helpers.memory import Memory
from python.helpers.dirty_json import DirtyJson
from agent import LoopData
from python.helpers.log import LogItem


class MemorizeSolutions(Extension):

    REPLACE_THRESHOLD = 0.9

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        # try:

        # show temp info message
        self.agent.context.log.log(
            type="info", content="Memorizing succesful solutions...", temp=True
        )

        # show full util message, this will hide temp message immediately if turned on
        log_item = self.agent.context.log.log(
            type="util",
            heading="Memorizing succesful solutions...",
        )

        # memorize in background
        asyncio.create_task(self.memorize(loop_data, log_item))

    async def memorize(self, loop_data: LoopData, log_item: LogItem, **kwargs):
        # get system message and chat history for util llm
        system = self.agent.read_prompt("memory.solutions_sum.sys.md")
        msgs_text = self.agent.concat_messages(self.agent.history)

        # log query streamed by LLM
        async def log_callback(content):
            log_item.stream(content=content)

        # call util llm to find solutions in history
        solutions_json = await self.agent.call_utility_model(
            system=system,
            message=msgs_text,
            callback=log_callback,
            background=True,
        )

        # Add validation and error handling for solutions_json
        if not solutions_json or not isinstance(solutions_json, str):
            log_item.update(heading="No response from utility model.")
            return

        # Strip any whitespace that might cause issues
        solutions_json = solutions_json.strip()

        if not solutions_json:
            log_item.update(heading="Empty response from utility model.")
            return

        try:
            solutions = DirtyJson.parse_string(solutions_json)
        except Exception as e:
            log_item.update(heading=f"Failed to parse solutions response: {str(e)}")
            return

        # Validate that solutions is a list or convertible to one
        if solutions is None:
            log_item.update(heading="No valid solutions found in response.")
            return

        # If solutions is not a list, try to make it one
        if not isinstance(solutions, list):
            if isinstance(solutions, (str, dict)):
                solutions = [solutions]
            else:
                log_item.update(heading="Invalid solutions format received.")
                return

        if not isinstance(solutions, list) or len(solutions) == 0:
            log_item.update(heading="No successful solutions to memorize.")
            return
        else:
            log_item.update(
                heading=f"{len(solutions)} successful solutions to memorize."
            )

        # Get the Memory Abstraction Layer
        memory_layer = await Memory.get_abstraction_layer(self.agent)

        solutions_txt = ""
        all_removed_docs = [] # To accumulate all docs removed across iterations
        for solution in solutions:
            # solution to plain text:
            if isinstance(solution, dict):
                problem = solution.get('problem', 'Unknown problem')
                solution_text = solution.get('solution', 'Unknown solution')
                txt = f"# Problem\n {problem}\n# Solution\n {solution_text}"
            else:
                # If solution is not a dict, convert it to string
                txt = f"# Solution\n {str(solution)}"
            solutions_txt += txt + "\n\n"

            # remove previous solutions too similiar to this one
            if self.REPLACE_THRESHOLD > 0:
                search_filter_solutions = {"area": Memory.Area.SOLUTIONS.value}
                removed_docs_for_current_solution = await memory_layer.delete_documents_by_query(
                    query=txt,
                    threshold=self.REPLACE_THRESHOLD,
                    filter=search_filter_solutions,
                )
                if removed_docs_for_current_solution:
                    all_removed_docs.extend(removed_docs_for_current_solution)
                    # Log accumulated removed docs at the end

            # insert new solution
            metadata_dict = {"area": Memory.Area.SOLUTIONS.value}
            # Add timestamp if standard, e.g.:
            # from datetime import datetime, timezone
            # metadata_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
            await memory_layer.insert_text(text=txt, metadata=metadata_dict)

        solutions_txt = solutions_txt.strip()
        log_item.update(solutions=solutions_txt)

        if all_removed_docs:
            rem_txt = "\n\n".join(Memory.format_docs_plain(all_removed_docs)) # type: ignore
            log_item.update(replaced=rem_txt)
            log_item.stream(result=f"\nReplaced {len(all_removed_docs)} previous solutions.")

        log_item.update(
            result=f"{len(solutions)} solutions memorized.",
            heading=f"{len(solutions)} solutions memorized.",
        )

    # except Exception as e:
    #     err = errors.format_error(e)
    #     self.agent.context.log.log(
    #         type="error", heading="Memorize solutions extension error:", content=err
    #     )
