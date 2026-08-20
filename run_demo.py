#!/usr/bin/env python3
"""
ACAS Quick Launcher
Starts the Web Dashboard or Interactive CLI.
"""

import sys
import os

if len(sys.argv) > 1 and sys.argv[1] == "cli":
    from cli import main
    main()
else:
    import uvicorn
    port = int(os.environ.get("PORT", 8090))
    print(f"🌐 Starting ACAS Universal Communication IR Learning Server on http://0.0.0.0:{port}")
    uvicorn.run("web.app:app", host="0.0.0.0", port=port, reload=False)
