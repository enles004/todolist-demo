from datetime import datetime

from flask import jsonify

from api.resource import GroupResource, ItemResource
from app import cache
from config import rabbitmq_config_project
from db.models import Project, Task
from db.session import db_session
from handlers.params import filtering, sorting
from services.connect_rabbitmq import RabbitMQ
from .middleware import check_permissions, g, jwt_required
from .schemas import ProjectPayload, ParamProject


class ProjectGroup(GroupResource):

    def _schema_params(self):
        return ParamProject()

    def _schema(self):
        return ProjectPayload()

    @jwt_required
    @check_permissions(["write"])
    def post(self, payload, path_params, query_params):
        new_project = Project(user_id=g.user_id, name=payload["name"])
        db_session.add(new_project)
        db_session.commit()
        data = self._schema().dump(new_project)
        return data, 201

    @jwt_required
    @check_permissions(["read"])
    # @cache.cached(timeout=20, key_prefix="projects-list")
    def get(self, payload, path_params, query_params):
        query = db_session.query(Project)
        # Pagination
        page = query_params["pagination"]["page"]
        per_page = query_params["pagination"]["per_page"]
        offset = (page - 1) * per_page

        # Filtering
        query = query.filter_by(user_id=g.user_id)
        if "filter" in query_params:
            filter_params = query_params["filter"]
            query = filtering(query=query, data_filter_params=filter_params, model=Project)

        # Sorting
        sort_params = query_params["sort"]
        try:
            query = sorting(query=query, data_sort_params=sort_params, model=Project)
        except AttributeError:
            return jsonify({"message": "invalid input attribute '{}'".format(sort_params["sort_by"])}), 400

        # Result
        total = query.count()
        products = query.offset(offset).limit(per_page).all()
        return {"data": [{"name": data.name, "id": data.id, "completed": data.completed} for data in products],
                "meta": [{"page": page, "per_page": per_page, "total": total}]}, 200


class ProjectItem(ItemResource):

    def _schema_params(self):
        return ParamProject()

    def _schema(self):
        return ProjectPayload()

    @jwt_required
    @check_permissions(["read"])
    @cache.cached(timeout=20, key_prefix="project-id")
    def get(self, payload, path_params, query_params):
        if query_params:
            project_params = db_session.query(Project).filter_by(user_id=g.user_id,
                                                                 id=path_params["id"],
                                                                 name=query_params["name"]).all()
            project_dump = ProjectPayload()
            data = project_dump.dump(project_params)
            return data, 200

        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"Message": "No project"}), 404
        data = self._schema().dump(project)
        return {"data": data}, 200

    @jwt_required
    @check_permissions(["write"])
    def put(self, payload, path_params, query_params):
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"Message": "Invalid"}), 401
        project.completed = True
        db_session.commit()
        if project.completed:
            data = ProjectPayload()
            return jsonify(data.dump(project)), 201
        return jsonify({"message": "error"}), 400

    @jwt_required
    @check_permissions(["write"])
    def delete(self, payload, path_params, query_params):
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"message": "no project"}), 404

        db_session.query(Task).filter(Task.project_id == path_params["id"]).delete()
        db_session.delete(project)
        now = datetime.now()
        time = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        db_session.commit()
        data = {"body": {"command_type": "send_mail_delete_project",
                         "email": g.email, "username": g.username,
                         "name": project.name, "deletion_date": str(time)},
                "routing_key": "delete-project"}
        RabbitMQ(**rabbitmq_config_project).publish(**data)
        return jsonify({"message": "deleted"}), 200
