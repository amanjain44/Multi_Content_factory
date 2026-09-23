import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run_e2e():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=120.0) as client:
        print("1. Creating Project...")
        project_res = await client.post("/api/projects", json={
            "title": "E2E Automated Project",
            "description": "Testing the full pipeline",
            "source_type": "idea",
            "source_reference": "A detailed video about AI"
        })
        project_res.raise_for_status()
        project = project_res.json()
        project_id = project["id"]
        print(f"Project created: {project_id}")

        print("2. Adding Source (Idea)...")
        source_res = await client.post(f"/api/projects/{project_id}/sources/ingest", data={
            "source_type": "text",
            "content": "A detailed video about the history of artificial intelligence and its impact on modern society."
        })
        source_res.raise_for_status()
        source = source_res.json()
        print(f"Source added: {source['id']}")

        print("3. Generating Content Selection...")
        cs_res = await client.post(f"/api/ai/content-selection", json={
            "project_id": project_id
        })
        cs_res.raise_for_status()
        cs_data = cs_res.json()
        
        print("4. Approving Content Selection...")
        opps = cs_data.get("opportunities", [])
        if not opps:
            raise Exception("No opportunities generated")
        opp_id = opps[0]["id"]
        
        cs_data["selected_id"] = opp_id
        
        app_res = await client.patch(f"/api/projects/{project_id}/stages/content-selection", json={
            "status": "Approved",
            "data": cs_data
        })
        app_res.raise_for_status()
        print("Content Selection approved.")

        print("5. Generating Platform Strategy...")
        ps_res = await client.post(f"/api/ai/platform-strategy", json={
            "project_id": project_id,
            "opportunity_id": opp_id
        })
        ps_res.raise_for_status()
        ps_data = ps_res.json()
        
        recs = ps_data.get("recommendations", [])
        plat_ids = [recs[0]["id"]] if recs else []
        ps_data["selected_ids"] = plat_ids
        
        await client.patch(f"/api/projects/{project_id}/stages/platform-strategy", json={
            "status": "Approved",
            "data": ps_data
        })
        print("Platform Strategy approved.")

        print("6. Generating Topic & Angle...")
        ta_res = await client.post(f"/api/ai/topic-angle", json={
            "project_id": project_id,
            "opportunity_id": opp_id,
            "platform_ids": plat_ids
        })
        ta_res.raise_for_status()
        ta_data = ta_res.json()
        
        angles = ta_data.get("angles", [])
        angle_id = angles[0]["id"] if angles else ""
        ta_data["selected_id"] = angle_id
        
        await client.patch(f"/api/projects/{project_id}/stages/topic-angle", json={
            "status": "Approved",
            "data": ta_data
        })
        print("Topic & Angle approved.")

        print("7. Generating Content Strategy...")
        cstrat_res = await client.post(f"/api/ai/content-strategy", json={
            "project_id": project_id,
            "opportunity_id": opp_id,
            "platform_ids": plat_ids,
            "angle_id": angle_id
        })
        cstrat_res.raise_for_status()
        cstrat_data = cstrat_res.json()
        
        await client.patch(f"/api/projects/{project_id}/stages/content-strategy", json={
            "status": "Approved",
            "data": cstrat_data
        })
        print("Content Strategy approved.")

        print("8. Generating Storyboard...")
        sb_res = await client.post(f"/api/ai/storyboard", json={
            "project_id": project_id
        })
        sb_res.raise_for_status()
        sb_data = sb_res.json()
        
        sb_data["storyboard"]["status"] = "Approved"
        await client.patch(f"/api/projects/{project_id}/stages/storyboard", json={
            "status": "Approved",
            "data": sb_data
        })
        print("Storyboard approved.")

        print("9. Generating Final Script...")
        fs_res = await client.post(f"/api/ai/script", json={
            "project_id": project_id
        })
        fs_res.raise_for_status()
        fs_data = fs_res.json()
        
        fs_data["script"]["status"] = "Completed"
        await client.patch(f"/api/projects/{project_id}/stages/script", json={
            "status": "Completed",
            "data": fs_data
        })
        print("Final Script approved and marked Completed.")

        print("10. Scheduling...")
        sch_res = await client.post(f"/api/schedules/", json={
            "project_id": project_id,
            "platform": "YouTube",
            "scheduled_at": "2026-10-01T12:00:00Z",
            "status": "Scheduled"
        })
        sch_res.raise_for_status()
        print("Project scheduled successfully.")
        
        print("11. Verifying Diagnostics...")
        diag_res = await client.get("/api/diagnostics/")
        diag_res.raise_for_status()
        diag = diag_res.json()
        print(f"Diagnostics fetched. AI Status: {diag['ai']['status']}")
        
        print("E2E Test Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(run_e2e())
