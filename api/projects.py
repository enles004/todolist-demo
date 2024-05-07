from datetime import datetime

from bson.objectid import ObjectId
from flask import jsonify

from api.resource import GroupResource, ItemResource
from db.session import projects, tasks
from handlers.params import filtering
from tasks import send_mail_delete
from .middleware import check_permissions, g, jwt_required
from api.schema.schema_project import ProjectPayload, ParamProject


class ProjectGroup(GroupResource):

    async def _schema_params(self):
        return ParamProject()

    async def _schema(self):
        return ProjectPayload()

    @jwt_required
    @check_permissions(["write"])
    async def post(self, payload, path_params, query_params):
        new_project = {"_id": str(ObjectId()), "user_id": g.user_id, "name": payload["name"], "action": False, "created": datetime.now()}
        projects.insert_one(new_project)
        schema = await self._schema()
        data = schema.dump(new_project)
        return data, 201

    @jwt_required
    @check_permissions(["read"])
    # @cache.cached(timeout=20, key_prefix="projects-list")
    async def get(self, payload, path_params, query_params):
        filters = {"user_id": g.user_id}
        # Pagination
        page = query_params["pagination"]["page"]
        per_page = query_params["pagination"]["per_page"]
        offset = (page - 1) * per_page

        # Filtering
        if "filter" in query_params:
            filter_params = query_params["filter"]
            filters.update(filtering(data_filter_params=filter_params))

        # Sorting
        sort_params = query_params["sort"]
        query = projects
        if sort_params["order"] == "asc":
            query = projects.find(filters).sort(sort_params["sort_by"], 1).skip(offset).limit(per_page)
        elif sort_params["order"] == "desc":
            query = projects.find(filters).sort(sort_params["sort_by"], -1).skip(offset).limit(per_page)

        # Result
        result = list(query)
        total = len(list(projects.find(filters).sort(sort_params["sort_by"], -1)))
        return {"data": [{"name": data["name"], "_id": data["_id"], "action": data["action"]} for data in result],
                "meta": [{"page": page, "per_page": per_page, "total": total}]}, 200


class ProjectItem(ItemResource):

    async def _schema_params(self):
        return ParamProject()

    async def _schema(self):
        return ProjectPayload()

    @jwt_required
    @check_permissions(["read"])
    # @cache.cached(timeout=20, key_prefix="project-id")
    async def get(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"Message": "No project"}), 404
        schema = await self._schema()
        data = schema.dump(project)
        return {"data": data}, 200

    @jwt_required
    @check_permissions(["write"])
    async def put(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"Message": "Invalid"}), 401
        new_action = {"$set": {"action": True}}
        update = projects.update_one({"user_id": g.user_id, "_id": path_params["id"]}, new_action)
        if update.raw_result["updatedExisting"]:
            after_project = project.find_one({"user_id": g.user_id, "_id": path_params["id"]})
            data = ProjectPayload()
            return jsonify(data.dump(after_project)), 201
        return jsonify({"message": "error"}), 400

    @jwt_required
    @check_permissions(["write"])
    async def delete(self, payload, path_params, query_params):
        project = projects.find_one({"user_id": g.user_id, "_id": path_params["id"]})
        if not project:
            return jsonify({"message": "no project"}), 404

        task = tasks.find_one({"project_id": path_params["id"]})
        if task:
            tasks.delete_many({"project_id": path_params["id"]})
        projects.delete_one({"user_id": g.user_id, "_id": path_params["id"]})
        now = datetime.now()
        time = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        data = {"email": g.email, "username": g.username, "name": project["name"], "deletion_date": str(time)}
        send_mail_delete.delay(data)
        return jsonify({"message": "deleted"}), 200
