"""
Reward API Blueprint
"""
from flask import Blueprint, request, jsonify
from app.models.reward import Reward
from app.schemas.reward_schema import RewardSchema, RewardCreateSchema
from app.services.reward_service import RewardService

bp = Blueprint('reward', __name__, url_prefix='/api/rewards')

schema = RewardSchema()
schemas = RewardSchema(many=True)
create_schema = RewardCreateSchema()


@bp.route('', methods=['GET'])
def get_list():
    """获取Reward列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = RewardService.get_all(page, per_page)

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
def get_one(item_id):
    """获取单个Reward"""
    item = RewardService.get_by_id(item_id)
    if not item:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    })


@bp.route('', methods=['POST'])
def create():
    """创建Reward"""
    data = request.get_json()

    errors = create_schema.validate(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    item = RewardService.create(data)

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    }), 201


@bp.route('/<int:item_id>', methods=['PUT'])
def update(item_id):
    """更新Reward"""
    data = request.get_json()

    item = RewardService.update(item_id, data)
    if not item:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    })


@bp.route('/<int:item_id>', methods=['DELETE'])
def delete(item_id):
    """删除Reward"""
    success = RewardService.delete(item_id)
    if not success:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({'success': True, 'message': '删除成功'})
