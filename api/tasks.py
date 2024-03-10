from datetime import datetime

from flask import jsonify

from api.resource import GroupResource, ItemResource
from app import cache
from db.models import Project, Task
from db.session import db_session
from .middleware import check_permissions, g, jwt_required
from .schemas import TaskPayload, ParamTask


class TasksGroup(GroupResource):

    def _schema_params(self):
        return ParamTask()

    def _schema(self):
        return TaskPayload()

    @jwt_required
    @check_permissions(["write"])
    def post(self, payload, path_params, query_params):
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"message": "no project"}), 404
        try:
            date = datetime.strptime(payload["expiry"], "%Y-%m-%d %H:%M:%S")
        except KeyError:
            now = datetime.now()
            date = datetime(now.year, now.month, now.day + 1)
        new_task = Task(project_id=path_params["id"],
                        title_task=payload['title'],
                        name_task=payload['name'],
                        expiry_task=date)

        db_session.add(new_task)
        db_session.commit()
        return jsonify(self._schema_params().dump(new_task)), 201

    @jwt_required
    @check_permissions(["read"])
    def get(self, payload, path_params, query_params):
        print('heh')
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"message": "no project"}), 404
        if query_params:
            query_params["project_id"] = project.id
            tasks = db_session.query(Task).filter_by(**query_params).all()
            task_dump = ParamTask(many=True)
            data = task_dump.dump(tasks)
            return data, 200

        tasks = db_session.query(Task).filter_by(project_id=project.id).all()
        task_dump = ParamTask(many=True)
        data = task_dump.dump(tasks)
        return data, 200


class TaskItem(ItemResource):

    def _schema(self):
        return ParamTask()

    def _schema_params(self):
        return TaskPayload()

    @jwt_required
    @check_permissions(["read"])
    @cache.cached(timeout=20, key_prefix="task-id")
    def get(self, payload, path_params, query_params):
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"message": "no project"}), 404
        if query_params:
            query_params["project_id"] = project.id
            task = db_session.query(Task).filter_by(**query_params).all()
            task_dump = ParamTask(many=True)
            data = task_dump.dump(task)
            return data, 200
        task = db_session.query(Task).filter_by(project_id=project.id, id=path_params["item_id"]).first()
        if not task:
            return jsonify({"message": "no task"}), 404
        task_dump = ParamTask()
        data = task_dump.dump(task)
        return {"data": data}, 200

    @jwt_required
    @check_permissions(["write"])
    def put(self, payload, path_params, query_params):
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()
        if not project:
            return jsonify({"message": "no project"}), 404
        task = db_session.query(Task).get(path_params["item_id"])
        if not task:
            return jsonify({"message": "no task"}), 404
        task.action_task = True
        task.date_completed = datetime.now()
        db_session.commit()
        if task.action_task:
            task_dump = ParamTask()
            return jsonify(task_dump.dump(task)), 201
        return jsonify({"message": "error"}), 400

    @jwt_required
    @check_permissions(["write"])
    def delete(self, payload, path_params, query_params):
        project = db_session.query(Project).filter_by(user_id=g.user_id, id=path_params["id"]).first()

        if not project:
            return jsonify({"message": "no project"}), 404

        task = db_session.query(Task).get(path_params["item_id"])
        if not task:
            return jsonify({"message": "no task"}), 404
        db_session.delete(path_params["item_id"])
        db_session.commit()
        return jsonify({"message": "deleted"}), 200
