from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os
import traceback
from typing import Optional
from typing import Dict, Any

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.db.database import PerformanceDB

db = PerformanceDB()

class Employee(BaseModel):
    name: str
    domain_account: str
    gender: str
    hometown: str
    university: str
    major: str
    phone: str
    id_card: str
    position: str
    join_date: str

@app.post('/api/employees')
async def create_employee(employee: Employee):
    """创建新员工"""
    try:
        with sqlite3.connect(db.db_path) as conn:
            # 获取全局配置的默认部门
            cursor = conn.execute("SELECT value FROM global_settings WHERE key = 'default_department'")
            default_department = cursor.fetchone()
            department = employee.department or (default_department[0] if default_department else None)
            
            conn.execute(
                "INSERT INTO employees (name, domain_account, gender, hometown, university, major, phone, department, position, join_date, id_card) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (employee.name, employee.domain_account, employee.gender, employee.hometown, 
                 employee.university, employee.major, employee.phone, department, 
                 employee.position, employee.join_date, employee.id_card)
            )
        return {"status": "success", "message": "员工信息添加成功"}
    except Exception as e:
        error_detail = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)