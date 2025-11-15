#!/usr/bin/env python3
"""
Supabase MCP Server for Claude Code
This server allows Claude to interact with Supabase database
"""

import json
import sys
from typing import Any, Dict, List
from database.supabase_client import SupabaseClient
from loguru import logger

class SupabaseMCPServer:
    """MCP Server for Supabase operations"""

    def __init__(self):
        self.client = SupabaseClient()
        logger.info("Supabase MCP Server initialized")

    def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        try:
            if method == "get_dashboard_stats":
                return self.client.get_dashboard_stats()

            elif method == "get_articles_for_dashboard":
                limit = params.get("limit", 50)
                min_priority = params.get("min_priority", 0)
                symbol = params.get("symbol")
                return self.client.get_articles_for_dashboard(limit, min_priority, symbol)

            elif method == "get_high_relevance_news":
                min_score = params.get("min_score", 70)
                limit = params.get("limit", 20)
                return self.client.get_high_relevance_news(min_score, limit)

            elif method == "get_trending_symbols":
                hours = params.get("hours", 24)
                limit = params.get("limit", 15)
                return self.client.get_trending_symbols(hours, limit)

            elif method == "get_signals_by_level":
                level = params.get("level", 1)
                hours = params.get("hours", 24)
                limit = params.get("limit", 50)
                return self.client.get_signals_by_level(level, hours, limit)

            elif method == "get_signals_by_symbol":
                symbol = params.get("symbol")
                hours = params.get("hours", 24)
                limit = params.get("limit", 20)
                if not symbol:
                    return {"error": "symbol parameter required"}
                return self.client.get_signals_by_symbol(symbol, hours, limit)

            elif method == "get_recent_articles":
                days = params.get("days", 7)
                limit = params.get("limit", 10)
                return self.client.get_recent_articles(days, limit)

            elif method == "get_important_symbols_today":
                return self.client.get_important_symbols_today()

            elif method == "get_price_impact_summary":
                hours = params.get("hours", 24)
                return self.client.get_price_impact_summary(hours)

            else:
                return {"error": f"Unknown method: {method}"}

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {"error": str(e)}

    def run(self):
        """Run MCP server (stdio mode)"""
        logger.info("MCP Server running in stdio mode")

        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                method = request.get("method")
                params = request.get("params", {})

                result = self.handle_request(method, params)

                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }

                print(json.dumps(response))
                sys.stdout.flush()

            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if "id" in request else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

if __name__ == "__main__":
    server = SupabaseMCPServer()
    server.run()
