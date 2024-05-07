from datetime import datetime

from bson.objectid import ObjectId
from flask import jsonify

from api.resource import GroupResource, ItemResource
from db.session import projects, tasks
from handlers.params import filtering
from .middleware import jwt_required, g, check_permissions
from api.schema.schema_task import TaskPayload, ParamTask, FiltrationTask


class TasksGroup(GroupResource):

    async def _schema_params(self):
        return ParamTask()

    async def _schema(self):
        return TaskPayload()

    @jwt_required
    @check_permissions(["write"])
    async def post(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"message": "no project"}), 404
        try:
            date = datetime.strptime(payload["expiry"], "%Y-%m-%d %H:%M:%S")
        except KeyError:
            now = datetime.now()
            date = datetime(now.year, now.month, now.day + 1)
        new_task = {"_id": str(ObjectId()),
                    "project_id": path_params["id"],
                    "title": payload['title'],
                    "name": payload['name'],
                    "expiry": date,
                    "action": False,
                    "date_complete": None,
                    "created": datetime.now()}

        tasks.insert_one(new_task)
        schema = FiltrationTask()
        data = schema.dump(new_task)
        return jsonify(data), 201

    @jwt_required
    @check_permissions(["read"])
    async def get(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"message": "no project"}), 404
        if query_params:
            # Pagination
            page = query_params["pagination"]["page"]
            per_page = query_params["pagination"]["per_page"]
            offset = (page - 1) * per_page

            # Filtering
            fil = {"project_id": project["_id"]}
            if "filter" in query_params:
                filter_params = query_params["filter"]
                fil.update(filtering(data_filter_params=filter_params))

            # Sorting
            sort_params = query_params["sort"]
            query = tasks
            if sort_params["order"] == "asc":
                query = tasks.find(fil).sort(sort_params["sort_by"], 1).skip(offset).limit(per_page)
            elif sort_params["order"] == "desc":
                query = tasks.find(fil).sort(sort_params["sort_by"], -1).skip(offset).limit(per_page)

            # Result
            result = list(query)
            total = len(result)
            return {"data": [
                {"title": data["title"], "name": data["name"], "created": data["created"], "id": str(data["_id"]),
                 "date_completed": data["date_complete"], "action": data["action"]} for data in result],
                    "meta": [{"page": page, "per_page": per_page, "total": total}]}, 200


class TaskItem(ItemResource):

    async def _schema(self):
        return ParamTask()

    async def _schema_params(self):
        return TaskPayload()

    @jwt_required
    @check_permissions(["read"])
    # @cache.cached(timeout=20, key_prefix="task-id")
    async def get(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"message": "no project"}), 404
        task = tasks.find_one({"project_id": project["_id"], "_id": path_params["item_id"]})
        if not task:
            return jsonify({"message": "no task"}), 404
        task_dump = FiltrationTask()
        data = task_dump.dump(task)
        return {"data": data}, 200

    @jwt_required
    @check_permissions(["write"])
    async def put(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"message": "no project"}), 404
        task = tasks.find_one({"_id": path_params["item_id"]})
        if not task:
            return jsonify({"message": "no task"}), 404
        update = {"$set": {"action": True, "date_complete": datetime.now()}}
        updated = task.update_one({"_id": path_params["item_id"]}, update)
        if updated.raw_result["updatedExisting"]:
            task_dump = FiltrationTask()
            return jsonify(task_dump.dump(task)), 201
        return jsonify({"message": "error"}), 400

    @jwt_required
    @check_permissions(["write"])
    async def delete(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})

        if not project:
            return jsonify({"message": "no project"}), 404

        task = tasks.find_one({"project_id": path_params["item_id"]})
        if not task:
            return jsonify({"message": "no task"}), 404
        task.delete_one({"project_id": path_params["item_id"]})
        return jsonify({"message": "deleted"}), 200
