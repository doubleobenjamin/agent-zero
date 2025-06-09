#!/usr/bin/env python3
"""
Enhanced Memory System Startup Script
Starts the required databases and validates the system
"""

import asyncio
import subprocess
import sys
import time
import os
from python.helpers.print_style import PrintStyle


def run_command(command, description):
    """Run a shell command and return success status"""
    try:
        PrintStyle.standard(f"🔄 {description}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            PrintStyle.standard(f"✅ {description} completed")
            return True
        else:
            PrintStyle.error(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        PrintStyle.error(f"❌ {description} failed: {e}")
        return False


def check_docker():
    """Check if Docker is available"""
    return run_command("docker --version", "Checking Docker availability")


def check_docker_compose():
    """Check if Docker Compose is available"""
    return run_command("docker-compose --version", "Checking Docker Compose availability")


def start_databases():
    """Start the enhanced memory databases"""
    PrintStyle.standard("\n🚀 Starting Enhanced Memory Databases")
    
    # Check if docker-compose.yml exists
    if not os.path.exists("docker-compose.yml"):
        PrintStyle.error("❌ docker-compose.yml not found in current directory")
        return False
    
    # Start databases
    if not run_command("docker-compose up -d", "Starting Qdrant and Neo4j databases"):
        return False
    
    # Wait for databases to be ready
    PrintStyle.standard("⏳ Waiting for databases to be ready...")
    time.sleep(10)
    
    # Check if services are running
    if not run_command("docker-compose ps", "Checking database status"):
        return False
    
    return True


def install_requirements():
    """Install required Python packages"""
    PrintStyle.standard("\n📦 Installing Enhanced Memory Requirements")
    
    # Install enhanced requirements
    commands = [
        "pip install qdrant-client>=1.12.0",
        "pip install graphiti-core>=0.3.0", 
        "pip install cognee>=0.1.0",
        "pip install neo4j>=5.0.0"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Installing {cmd.split()[2]}"):
            PrintStyle.error(f"❌ Failed to install {cmd.split()[2]}")
            PrintStyle.standard("💡 You may need to install manually or check your Python environment")
    
    return True


async def validate_system():
    """Validate the enhanced memory system"""
    PrintStyle.standard("\n🧪 Validating Enhanced Memory System")
    
    try:
        # Import and run the test
        from test_enhanced_memory import test_enhanced_memory
        return await test_enhanced_memory()
    except ImportError as e:
        PrintStyle.error(f"❌ Cannot import test module: {e}")
        return False
    except Exception as e:
        PrintStyle.error(f"❌ Validation failed: {e}")
        return False


async def main():
    """Main startup function"""
    PrintStyle.standard("🚀 Enhanced Memory System Startup")
    PrintStyle.standard("=" * 50)
    PrintStyle.standard("Phase 1, Agent 1: Enhanced Memory System Implementation")
    PrintStyle.standard("")
    
    # Step 1: Check prerequisites
    PrintStyle.standard("📋 Step 1: Checking Prerequisites")
    
    if not check_docker():
        PrintStyle.error("❌ Docker is required but not available")
        PrintStyle.standard("💡 Please install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    if not check_docker_compose():
        PrintStyle.error("❌ Docker Compose is required but not available")
        PrintStyle.standard("💡 Please install Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    # Step 2: Install requirements
    PrintStyle.standard("\n📦 Step 2: Installing Requirements")
    install_requirements()
    
    # Step 3: Start databases
    PrintStyle.standard("\n🗄️ Step 3: Starting Databases")
    if not start_databases():
        PrintStyle.error("❌ Failed to start databases")
        PrintStyle.standard("💡 Try running manually: docker-compose up -d")
        sys.exit(1)
    
    # Step 4: Validate system
    PrintStyle.standard("\n✅ Step 4: Validating System")
    success = await validate_system()
    
    if success:
        PrintStyle.standard("\n🎉 SUCCESS: Enhanced Memory System is ready!")
        PrintStyle.standard("")
        PrintStyle.standard("🔧 What's been set up:")
        PrintStyle.standard("   • Qdrant vector database (localhost:6333)")
        PrintStyle.standard("   • Neo4j graph database (localhost:7687)")
        PrintStyle.standard("   • Enhanced memory tools with entity extraction")
        PrintStyle.standard("   • Hybrid search across all systems")
        PrintStyle.standard("")
        PrintStyle.standard("🎯 Next steps:")
        PrintStyle.standard("   • Start Agent Zero normally")
        PrintStyle.standard("   • Use memory_save tool to store information")
        PrintStyle.standard("   • Use memory_load tool with search_type options")
        PrintStyle.standard("   • Use memory_insights tool to see system stats")
        PrintStyle.standard("")
        PrintStyle.standard("✅ Phase 1, Agent 1 implementation complete!")
    else:
        PrintStyle.error("\n❌ STARTUP FAILED")
        PrintStyle.standard("💡 Check the errors above and try again")
        PrintStyle.standard("💡 You can also run: python test_enhanced_memory.py")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
