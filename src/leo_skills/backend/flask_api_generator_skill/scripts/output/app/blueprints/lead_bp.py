"""
Lead API Blueprint
"""
from flask import Blueprint, request, jsonify
from app.models.lead import Lead
from app.schemas.lead_schema import LeadSchema, LeadCreateSchema
from app.services.lead_service import LeadService

bp = Blueprint('lead', __name__, url_prefix='/api/leads')

schema = LeadSchema()
schemas = LeadSchema(many=True)
create_schema = LeadCreateSchema()


@bp.route('', methods=['GET'])
def get_list():
    """获取Lead列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = LeadService.get_all(page, per_page)

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
    """获取单个Lead"""
    item = LeadService.get_by_id(item_id)
    if not item:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    })


@bp.route('', methods=['POST'])
def create():
    """创建Lead"""
    data = request.get_json()

    errors = create_schema.validate(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    item = LeadService.create(data)

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    }), 201


@bp.route('/<int:item_id>', methods=['PUT'])
def update(item_id):
    """更新Lead"""
    data = request.get_json()

    item = LeadService.update(item_id, data)
    if not item:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({
        'success': True,
        'data': schema.dump(item)
    })


@bp.route('/<int:item_id>', methods=['DELETE'])
def delete(item_id):
    """删除Lead"""
    success = LeadService.delete(item_id)
    if not success:
        return jsonify({'success': False, 'error': '未找到'}), 404

    return jsonify({'success': True, 'message': '删除成功'})
