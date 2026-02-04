"""
User API Blueprint
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.schemas.user_schema import UserSchema, UserCreateSchema
from app.services.user_service import UserService

bp = Blueprint('user', __name__, url_prefix='/api/users')

schema = UserSchema()
schemas = UserSchema(many=True)
create_schema = UserCreateSchema()


@bp.route('', methods=['GET'])
@jwt_required()
    def get_list():
    """获取User列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = UserService.get_all(page, per_page)

    return jsonify({
        'success': True,
        'data': schemas.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
    def get_one(item_id):
    """获取单个User"""
    item = UserService.get_by_id(item_id)
    if not item:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    })


@bp.route('', methods=['POST'])
@jwt_required()
    def create():
    """创建User"""
    data = request.get_json()

    errors = create_schema.validate(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    item = UserService.create(data)

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    }), 201


@bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
    def update(item_id):
    """更新User"""
    data = request.get_json()

    item = UserService.update(item_id, data)
    if not item:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    })


@bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
    def delete(item_id):
    """删除User"""
    success = UserService.delete(item_id)
    if not success:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({'success': True, 'message': '删除成功'})
