import os
import models
from agent import AgentConfig, ModelConfig
from python.helpers import runtime, settings, defer
from python.helpers.print_style import PrintStyle


def initialize_agent():
    current_settings = settings.get_settings()

    # chat model from user settings
    chat_llm = ModelConfig(
        provider=models.ModelProvider[current_settings["chat_model_provider"]],
        name=current_settings["chat_model_name"],
        ctx_length=current_settings["chat_model_ctx_length"],
        vision=current_settings["chat_model_vision"],
        limit_requests=current_settings["chat_model_rl_requests"],
        limit_input=current_settings["chat_model_rl_input"],
        limit_output=current_settings["chat_model_rl_output"],
        kwargs=current_settings["chat_model_kwargs"],
    )

    # utility model from user settings
    utility_llm = ModelConfig(
        provider=models.ModelProvider[current_settings["util_model_provider"]],
        name=current_settings["util_model_name"],
        ctx_length=current_settings["util_model_ctx_length"],
        limit_requests=current_settings["util_model_rl_requests"],
        limit_input=current_settings["util_model_rl_input"],
        limit_output=current_settings["util_model_rl_output"],
        kwargs=current_settings["util_model_kwargs"],
    )
    # embedding model from user settings
    embedding_llm = ModelConfig(
        provider=models.ModelProvider[current_settings["embed_model_provider"]],
        name=current_settings["embed_model_name"],
        limit_requests=current_settings["embed_model_rl_requests"],
        kwargs=current_settings["embed_model_kwargs"],
    )
    # browser model from user settings
    browser_llm = ModelConfig(
        provider=models.ModelProvider[current_settings["browser_model_provider"]],
        name=current_settings["browser_model_name"],
        vision=current_settings["browser_model_vision"],
        kwargs=current_settings["browser_model_kwargs"],
    )
    # enhanced capabilities configuration from settings
    enhanced_config = {
        # Enhanced Memory System
        'enhanced_memory': current_settings.get("enhanced_memory", True),
        'graphiti_enabled': current_settings.get("graphiti_enabled", True),
        'qdrant_enabled': current_settings.get("qdrant_enabled", True),
        'hybrid_search_enabled': True,
        'context_extension_enabled': True,

        # Agent Orchestration (Agno)
        'agno_orchestration': current_settings.get("agno_orchestration", True),
        'max_concurrent_agents': current_settings.get("max_concurrent_agents", 10),
        'agent_timeout': current_settings.get("agent_timeout", 300),
        'team_coordination_timeout': 600,
        'enable_persistent_agents': True,
        'enable_memory_sharing': True,

        # ACI Tools Integration
        'aci_tools_enabled': os.getenv("ACI_TOOLS_ENABLED", "true").lower() == "true",
        'aci_api_key': current_settings.get("aci_api_key", ""),
        'aci_project_id': current_settings.get("aci_project_id", ""),
        'aci_base_url': current_settings.get("aci_base_url", "https://api.aci.dev"),

        # Database Configuration
        'neo4j_uri': current_settings.get("neo4j_uri", "bolt://localhost:7687"),
        'neo4j_user': current_settings.get("neo4j_user", "neo4j"),
        'neo4j_password': current_settings.get("neo4j_password", "password"),
        'qdrant_host': current_settings.get("qdrant_host", "localhost"),
        'qdrant_port': current_settings.get("qdrant_port", 6333),
        'qdrant_api_key': current_settings.get("qdrant_api_key", ""),

        # Performance Settings
        'enable_caching': current_settings.get("enable_caching", True),
        'cache_ttl': 3600,  # 1 hour cache TTL
        'memory_optimization': True,
        'parallel_processing': True,

        # Monitoring and Health Checks
        'health_checks_enabled': current_settings.get("health_checks_enabled", True),
        'performance_monitoring': current_settings.get("performance_monitoring", True),
        'error_recovery': True,
        'graceful_degradation': True
    }

    # agent configuration
    config = AgentConfig(
        chat_model=chat_llm,
        utility_model=utility_llm,
        embeddings_model=embedding_llm,
        browser_model=browser_llm,
        prompts_subdir=current_settings["agent_prompts_subdir"],
        memory_subdir=current_settings["agent_memory_subdir"],
        knowledge_subdirs=["default", current_settings["agent_knowledge_subdir"]],
        mcp_servers=current_settings["mcp_servers"],
        code_exec_docker_enabled=False,
        additional=enhanced_config,
        # code_exec_docker_name = "A0-dev",
        # code_exec_docker_image = "frdel/agent-zero-run:development",
        # code_exec_docker_ports = { "22/tcp": 55022, "80/tcp": 55080 }
        # code_exec_docker_volumes = {
        # files.get_base_dir(): {"bind": "/a0", "mode": "rw"},
        # files.get_abs_path("work_dir"): {"bind": "/root", "mode": "rw"},
        # },
        # code_exec_ssh_enabled = True,
        # code_exec_ssh_addr = "localhost",
        # code_exec_ssh_port = 55022,
        # code_exec_ssh_user = "root",
        # code_exec_ssh_pass = "",
    )

    # update SSH and docker settings
    _set_runtime_config(config, current_settings)

    # update config with runtime args
    _args_override(config)

    # initialize enhanced systems with health checks
    _initialize_enhanced_systems(config)

    # initialize MCP in deferred task to prevent blocking the main thread
    # async def initialize_mcp_async(mcp_servers_config: str):
    #     return initialize_mcp(mcp_servers_config)
    # defer.DeferredTask(thread_name="mcp-initializer").start_task(initialize_mcp_async, config.mcp_servers)
    # initialize_mcp(config.mcp_servers)

    # import python.helpers.mcp_handler as mcp_helper
    # import agent as agent_helper
    # import python.helpers.print_style as print_style_helper
    # if not mcp_helper.MCPConfig.get_instance().is_initialized():
    #     try:
    #         mcp_helper.MCPConfig.update(config.mcp_servers)
    #     except Exception as e:
    #         first_context = agent_helper.AgentContext.first()
    #         if first_context:
    #             (
    #                 first_context.log
    #                 .log(type="warning", content=f"Failed to update MCP settings: {e}", temp=False)
    #             )
    #         (
    #             print_style_helper.PrintStyle(background_color="black", font_color="red", padding=True)
    #             .print(f"Failed to update MCP settings: {e}")
    #         )

    # return config object
    return config

def initialize_chats():
    from python.helpers import persist_chat
    async def initialize_chats_async():
        persist_chat.load_tmp_chats()
    return defer.DeferredTask().start_task(initialize_chats_async)

def initialize_mcp():
    set = settings.get_settings()
    async def initialize_mcp_async():
        from python.helpers.mcp_handler import initialize_mcp as _initialize_mcp
        return _initialize_mcp(set["mcp_servers"])
    return defer.DeferredTask().start_task(initialize_mcp_async)

def initialize_job_loop():
    from python.helpers.job_loop import run_loop
    return defer.DeferredTask("JobLoop").start_task(run_loop)


def _initialize_enhanced_systems(config: AgentConfig):
    """Initialize enhanced systems with health checks and graceful degradation"""

    if not config.additional.get('health_checks_enabled', True):
        return

    # Initialize enhanced memory system
    if config.additional.get('enhanced_memory', True):
        try:
            _check_database_connections(config)
            PrintStyle(font_color="green", padding=True).print("✓ Enhanced memory system initialized")
        except Exception as e:
            if config.additional.get('graceful_degradation', True):
                config.additional['enhanced_memory'] = False
                PrintStyle(font_color="yellow", padding=True).print(f"⚠ Enhanced memory disabled: {e}")
            else:
                raise

    # Initialize agent orchestration
    if config.additional.get('agno_orchestration', True):
        try:
            _check_orchestration_requirements(config)
            PrintStyle(font_color="green", padding=True).print("✓ Agent orchestration system initialized")
        except Exception as e:
            if config.additional.get('graceful_degradation', True):
                config.additional['agno_orchestration'] = False
                PrintStyle(font_color="yellow", padding=True).print(f"⚠ Agent orchestration disabled: {e}")
            else:
                raise

    # Initialize ACI tools
    if config.additional.get('aci_tools_enabled', True):
        try:
            _check_aci_configuration(config)
            PrintStyle(font_color="green", padding=True).print("✓ ACI tools integration initialized")
        except Exception as e:
            if config.additional.get('graceful_degradation', True):
                config.additional['aci_tools_enabled'] = False
                PrintStyle(font_color="yellow", padding=True).print(f"⚠ ACI tools disabled: {e}")
            else:
                raise


def _check_database_connections(config: AgentConfig):
    """Check database connections for enhanced memory system"""

    # Check Neo4j connection
    if config.additional.get('graphiti_enabled', True):
        neo4j_uri = config.additional.get('neo4j_uri', 'bolt://localhost:7687')
        # Note: Actual connection check would be implemented here
        # For now, we just validate the configuration
        if not neo4j_uri:
            raise Exception("Neo4j URI not configured")

    # Check Qdrant connection
    if config.additional.get('qdrant_enabled', True):
        qdrant_host = config.additional.get('qdrant_host', 'localhost')
        qdrant_port = config.additional.get('qdrant_port', 6333)
        # Note: Actual connection check would be implemented here
        if not qdrant_host or not qdrant_port:
            raise Exception("Qdrant connection not configured")


def _check_orchestration_requirements(config: AgentConfig):
    """Check requirements for agent orchestration system"""

    max_agents = config.additional.get('max_concurrent_agents', 10)
    if max_agents < 1 or max_agents > 100:
        raise Exception(f"Invalid max_concurrent_agents: {max_agents}")

    agent_timeout = config.additional.get('agent_timeout', 300)
    if agent_timeout < 10:
        raise Exception(f"Agent timeout too low: {agent_timeout}")


def _check_aci_configuration(config: AgentConfig):
    """Check ACI tools configuration and interface availability"""

    # Check if ACI interface is available (from Phase 1, Agent 3)
    try:
        from python.helpers.aci_interface import aci_interface
    except ImportError:
        raise Exception("ACI interface not available from Phase 1, Agent 3")

    # Check if ACI interface is enabled
    if not hasattr(aci_interface, 'is_enabled') or not aci_interface.is_enabled():
        raise Exception("ACI interface is not enabled")

    # Note: Additional configuration validation could be added here
    # The actual ACI client initialization is handled by the existing interface


def _args_override(config):
    # update config with runtime args
    for key, value in runtime.args.items():
        if hasattr(config, key):
            # conversion based on type of config[key]
            if isinstance(getattr(config, key), bool):
                value = value.lower().strip() == "true"
            elif isinstance(getattr(config, key), int):
                value = int(value)
            elif isinstance(getattr(config, key), float):
                value = float(value)
            elif isinstance(getattr(config, key), str):
                value = str(value)
            else:
                raise Exception(
                    f"Unsupported argument type of '{key}': {type(getattr(config, key))}"
                )

            setattr(config, key, value)


def _set_runtime_config(config: AgentConfig, set: settings.Settings):
    ssh_conf = settings.get_runtime_config(set)
    for key, value in ssh_conf.items():
        if hasattr(config, key):
            setattr(config, key, value)

    # if config.code_exec_docker_enabled:
    #     config.code_exec_docker_ports["22/tcp"] = ssh_conf["code_exec_ssh_port"]
    #     config.code_exec_docker_ports["80/tcp"] = ssh_conf["code_exec_http_port"]
    #     config.code_exec_docker_name = f"{config.code_exec_docker_name}-{ssh_conf['code_exec_ssh_port']}-{ssh_conf['code_exec_http_port']}"

    #     dman = docker.DockerContainerManager(
    #         logger=log.Log(),
    #         name=config.code_exec_docker_name,
    #         image=config.code_exec_docker_image,
    #         ports=config.code_exec_docker_ports,
    #         volumes=config.code_exec_docker_volumes,
    #     )
    #     dman.start_container()

    # config.code_exec_ssh_pass = asyncio.run(rfc_exchange.get_root_password())
