import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from models import db, Ingrediente, FichaTecnica, FichaTecnicaIngrediente, Forma, Configuracao
from sqlalchemy import or_, and_


# --- Configuração Inicial ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///confeitando_com_artes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil'
db.init_app(app)

@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    print('Banco de dados inicializado com sucesso!')

# --- Rotas Principais ---

@app.route('/')
def index():
    """Página Inicial / Dashboard com Gráfico e Alertas de Estoque"""
    # Lógica para o Gráfico (continua igual)
    ingredientes_estoque_grafico = Ingrediente.query.order_by(Ingrediente.quantidade_estoque.desc()).limit(10).all()
    labels_grafico = [ing.nome for ing in ingredientes_estoque_grafico]
    dados_grafico = [ing.quantidade_estoque for ing in ingredientes_estoque_grafico]
    total_fichas = FichaTecnica.query.count()

    # --- NOVA LÓGICA PARA BUSCAR ITENS COM ESTOQUE BAIXO ---
    # As mesmas regras de cores que usamos antes
    condicao_critica = or_(
        and_(Ingrediente.unidade_medida.in_(['g', 'ml']), Ingrediente.quantidade_estoque <= 100),
        and_(Ingrediente.unidade_medida == 'unid', Ingrediente.quantidade_estoque <= 5)
    )
    condicao_alerta = or_(
        and_(Ingrediente.unidade_medida.in_(['g', 'ml']), Ingrediente.quantidade_estoque > 100, Ingrediente.quantidade_estoque <= 500),
        and_(Ingrediente.unidade_medida == 'unid', Ingrediente.quantidade_estoque > 5, Ingrediente.quantidade_estoque <= 15)
    )
    
    # Busca todos os ingredientes que se encaixam em qualquer uma das condições
    ingredientes_pouco_estoque = Ingrediente.query.filter(
        or_(condicao_critica, condicao_alerta)
    ).order_by(Ingrediente.quantidade_estoque.asc()).all()
    
    # Passamos a nova lista para o template
    return render_template('index.html', 
                           total_fichas=total_fichas,
                           labels_grafico=labels_grafico,
                           dados_grafico=dados_grafico,
                           alertas_estoque=ingredientes_pouco_estoque)
# Em app.py

@app.route('/ingredientes', methods=['GET', 'POST'])
def gerenciar_ingredientes():
    if request.method == 'POST':
        # A lógica para ADICIONAR um ingrediente continua a mesma
        nome = request.form['nome'].strip()
        if Ingrediente.query.filter(db.func.lower(Ingrediente.nome) == db.func.lower(nome)).first():
            flash(f'Erro: O ingrediente "{nome}" já está cadastrado.', 'danger')
            return redirect(url_for('gerenciar_ingredientes'))

        tipo_preco = request.form['tipo_preco']
        preco_informado = float(request.form.get('preco', 0) or 0)
        unidades_compradas = int(request.form.get('unidades_compradas', 1) or 1)
        tamanho_unidade = float(request.form.get('tamanho_unidade', 0) or 0)

        if tipo_preco == 'total':
            preco_total_pago = preco_informado
        else:
            preco_total_pago = preco_informado * unidades_compradas
        
        estoque_inicial = tamanho_unidade * unidades_compradas
        custo_inicial = 0
        if estoque_inicial > 0:
            custo_inicial = preco_total_pago / estoque_inicial
        
        novo_ingrediente = Ingrediente(
            nome=nome,
            marca=request.form['marca'],
            unidade_medida=request.form['unidade_medida'],
            quantidade_estoque=estoque_inicial,
            custo_medio_por_unidade_base=custo_inicial
        )
        
        db.session.add(novo_ingrediente)
        db.session.commit()
        flash(f'Ingrediente "{nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('gerenciar_ingredientes'))

    # --- LÓGICA DE PAGINAÇÃO (MUDANÇA AQUI) ---
    # 1. Pega o número da página da URL (ex: /ingredientes?page=2), o padrão é 1.
    page = request.args.get('page', 1, type=int)
    
    # 2. Em vez de .all(), usamos .paginate()
    paginacao = Ingrediente.query.order_by(Ingrediente.nome).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # 3. Os itens da página atual estão em paginacao.items
    ingredientes_da_pagina = paginacao.items
    
    # 4. Passamos o objeto de paginação completo para o template
    return render_template('ingredientes.html', ingredientes=ingredientes_da_pagina, paginacao=paginacao)



@app.route('/formas', methods=['GET', 'POST'])
def gerenciar_formas():
    if request.method == 'POST':
        descricao = request.form['descricao'].strip()
        if Forma.query.filter(db.func.lower(Forma.descricao) == db.func.lower(descricao)).first():
            flash(f'Erro: A forma "{descricao}" já está cadastrada.', 'danger')
        else:
            nova_forma = Forma(descricao=descricao)
            db.session.add(nova_forma)
            db.session.commit()
            flash('Forma adicionada com sucesso!', 'success')
        return redirect(url_for('gerenciar_formas'))
    
    formas = Forma.query.order_by(Forma.descricao).all()
    return render_template('formas.html', formas=formas)

@app.route('/configuracoes', methods=['GET', 'POST'])
def gerenciar_configuracoes():
    # Garante que sempre exista um registro de configuração com id=1
    config = Configuracao.query.get(1)
    if not config:
        config = Configuracao(id=1)
        db.session.add(config)
        db.session.commit()

    if request.method == 'POST':
        # Pega os dados do formulário e atualiza o objeto de configuração
        config.salario_desejado = float(request.form.get('salario_desejado', 0) or 0)
        config.custo_gas = float(request.form.get('custo_gas', 0) or 0)
        config.custo_luz = float(request.form.get('custo_luz', 0) or 0)
        config.custo_agua = float(request.form.get('custo_agua', 0) or 0)
        config.custo_outros = float(request.form.get('custo_outros', 0) or 0)
        config.horas_por_dia = float(request.form.get('horas_por_dia', 0) or 0)
        config.dias_por_semana = int(request.form.get('dias_por_semana', 0) or 0)
        
        # Chama o método para recalcular o custo da hora
        config.calcular_custo_hora()
        
        db.session.commit()
        flash('Configurações salvas e custo da hora atualizado!', 'success')
        return redirect(url_for('gerenciar_configuracoes'))
        
    return render_template('configuracoes.html', config=config)

#editar ingrediente
@app.route('/ingrediente/edit/<int:ingrediente_id>', methods=['GET', 'POST'])
def editar_ingrediente(ingrediente_id):
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    if request.method == 'POST':
        novo_nome = request.form['nome'].strip()
        
        # Verifica se o novo nome já existe em outro ingrediente
        outro_ingrediente_com_mesmo_nome = Ingrediente.query.filter(Ingrediente.id != ingrediente_id, db.func.lower(Ingrediente.nome) == db.func.lower(novo_nome)).first()
        if outro_ingrediente_com_mesmo_nome:
            flash('Erro: Já existe outro ingrediente com este nome.', 'danger')
        else:
            ingrediente.nome = novo_nome
            ingrediente.marca = request.form['marca']
            db.session.commit()
            flash('Ingrediente atualizado com sucesso!', 'success')
            return redirect(url_for('gerenciar_ingredientes'))
            
    return render_template('editar_ingrediente.html', ingrediente=ingrediente)

@app.route('/ingrediente/delete/<int:ingrediente_id>', methods=['POST'])
def deletar_ingrediente(ingrediente_id):
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    
    # Adicionar verificação se o ingrediente está em uso no futuro
    
    db.session.delete(ingrediente)
    db.session.commit()
    flash(f'Ingrediente "{ingrediente.nome}" foi excluído.', 'success')
    return redirect(url_for('gerenciar_ingredientes'))




@app.route('/fichas-tecnicas', methods=['GET', 'POST'])
def gerenciar_fichas_tecnicas():
    if request.method == 'POST':
        nome = request.form['nome']
        nova_ficha = FichaTecnica(nome=nome, rendimento=request.form['rendimento'], observacoes=request.form['observacoes'])
        db.session.add(nova_ficha)
        db.session.commit()
        flash('Ficha Técnica criada com sucesso!', 'success')
        return redirect(url_for('gerenciar_fichas_tecnicas'))
    
    fichas_tecnicas = FichaTecnica.query.order_by(FichaTecnica.nome).all()
    return render_template('fichas_tecnicas.html', fichas_tecnicas=fichas_tecnicas)

@app.route('/ficha-tecnica/<int:ficha_tecnica_id>', methods=['GET', 'POST'])
def detalhe_ficha_tecnica(ficha_tecnica_id):
    ficha = FichaTecnica.query.get_or_404(ficha_tecnica_id)
    todos_ingredientes = Ingrediente.query.order_by(Ingrediente.nome).all()
    todas_formas = Forma.query.order_by(Forma.descricao).all()

    if request.method == 'POST':
        # Lógica para adicionar ingrediente (continua igual)
        if 'ingrediente_id' in request.form:
            ingrediente_id = request.form.get('ingrediente_id')
            quantidade_usada = request.form.get('quantidade_usada')
            if ingrediente_id and quantidade_usada:
                nova_associacao = FichaTecnicaIngrediente(fichatecnica_id=ficha.id, ingrediente_id=int(ingrediente_id), quantidade_usada=float(quantidade_usada))
                db.session.add(nova_associacao)
                db.session.commit()
                flash('Ingrediente adicionado à ficha!', 'success')
        if 'atualizar_ficha' in request.form:
            ficha.rendimento = request.form.get('rendimento')
            ficha.observacoes = request.form.get('observacoes')
            
            peso_str = request.form.get('peso_final_gramas')
            ficha.peso_final_gramas = float(peso_str) if peso_str else None
            
            # --- SALVANDO OS NOVOS CAMPOS ---
            tempo_str = request.form.get('tempo_producao_minutos')
            ficha.tempo_producao_minutos = int(tempo_str) if tempo_str else 0
            
            # Um checkbox não enviado tem valor 'None'. Se for enviado, tem valor 'on'.
            ficha.incluir_custo_mao_de_obra = request.form.get('incluir_custo_mao_de_obra') == 'on'
            # --- FIM DO NOVO TRECHO ---

            ids_formas_selecionadas = request.form.getlist('formas_selecionadas')
            ficha.formas = [Forma.query.get(id_forma) for id_forma in ids_formas_selecionadas]
            
            db.session.commit()
            flash('Ficha Técnica atualizada com sucesso!', 'info')

        return redirect(url_for('detalhe_ficha_tecnica', ficha_tecnica_id=ficha.id))

    return render_template('ficha_tecnica_detalhe.html', ficha=ficha, todos_ingredientes=todos_ingredientes, todas_formas=todas_formas)


@app.route('/ingrediente/adicionar-estoque/<int:ingrediente_id>', methods=['POST'])
def adicionar_estoque(ingrediente_id):
    """Registra uma nova compra e recalcula o custo médio ponderado."""
    ingrediente = Ingrediente.query.get_or_404(ingrediente_id)
    
    # Dados da NOVA compra
    preco_lote = float(request.form.get('preco_lote', 0) or 0)
    unidades_lote = int(request.form.get('unidades_lote', 1) or 1)
    tamanho_unidade_lote = float(request.form.get('tamanho_unidade_lote', 0) or 0)

    if preco_lote <= 0 or tamanho_unidade_lote <= 0:
        flash('Valores inválidos para a nova compra.', 'danger')
        return redirect(url_for('gerenciar_ingredientes'))

    # Valores do estoque ANTIGO
    estoque_antigo_total = ingrediente.quantidade_estoque
    custo_medio_antigo = ingrediente.custo_medio_por_unidade_base
    valor_total_estoque_antigo = estoque_antigo_total * custo_medio_antigo

    # Valores do estoque NOVO
    quantidade_adicionada = tamanho_unidade_lote * unidades_lote
    valor_total_estoque_novo = preco_lote

    # Cálculo do Custo Médio Ponderado
    novo_estoque_total = estoque_antigo_total + quantidade_adicionada
    novo_valor_total = valor_total_estoque_antigo + valor_total_estoque_novo
    
    novo_custo_medio = 0
    if novo_estoque_total > 0:
        novo_custo_medio = novo_valor_total / novo_estoque_total
    
    # Atualiza o ingrediente
    ingrediente.quantidade_estoque = novo_estoque_total
    ingrediente.custo_medio_por_unidade_base = novo_custo_medio
    
    db.session.commit()
    flash(f'Estoque de "{ingrediente.nome}" atualizado! Novo custo médio: R$ {novo_custo_medio:.4f}', 'success')
    return redirect(url_for('gerenciar_ingredientes'))

@app.route('/ficha-tecnica/ingrediente/delete/<int:item_id>', methods=['POST'])
def deletar_item_ficha(item_id):
    item_para_deletar = FichaTecnicaIngrediente.query.get_or_404(item_id)
    ficha_tecnica_id = item_para_deletar.fichatecnica_id
    db.session.delete(item_para_deletar)
    db.session.commit()
    flash('Ingrediente removido da ficha.', 'success')
    return redirect(url_for('detalhe_ficha_tecnica', ficha_tecnica_id=ficha_tecnica_id))

@app.route('/ficha-tecnica/delete/<int:ficha_tecnica_id>', methods=['POST'])
def deletar_ficha_tecnica(ficha_tecnica_id):
    ficha = FichaTecnica.query.get_or_404(ficha_tecnica_id)
    db.session.delete(ficha)
    db.session.commit()
    flash(f'Ficha Técnica "{ficha.nome}" deletada com sucesso.', 'warning')
    return redirect(url_for('gerenciar_fichas_tecnicas'))

@app.route('/exportar/ficha-tecnica/<int:ficha_tecnica_id>')
def exportar_ficha_tecnica(ficha_tecnica_id):
    ficha = FichaTecnica.query.get_or_404(ficha_tecnica_id)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Ficha Técnica'
    bold_font = Font(bold=True, size=12)
    title_font = Font(bold=True, size=16)
    center_align = Alignment(horizontal='center', vertical='center')
    right_align = Alignment(horizontal='right')
    sheet.merge_cells('A1:E1')
    title_cell = sheet['A1']
    title_cell.value = f"Ficha Técnica - {ficha.nome}"
    title_cell.font = title_font
    title_cell.alignment = center_align
    sheet.row_dimensions[1].height = 25
    sheet['A3'] = "Rendimento:"
    sheet['A3'].font = bold_font
    sheet['B3'] = ficha.rendimento
    sheet['A4'] = "Formas Utilizadas:"
    sheet['A4'].font = bold_font
    sheet['B4'] = ", ".join([forma.descricao for forma in ficha.formas])
    sheet.append(['']); sheet.append([''])
    headers = ['Ingrediente', 'Marca', 'Quantidade Usada', 'Unidade', 'Custo do Item (R$)']
    sheet.append(headers)
    for cell in sheet[7]:
        cell.font = bold_font
    for item in ficha.ingredientes:
        custo_item = item.ingrediente.preco_por_unidade() * item.quantidade_usada
        sheet.append([
            item.ingrediente.nome, item.ingrediente.marca,
            item.quantidade_usada, item.ingrediente.unidade_medida,
            round(custo_item, 2)
        ])
    sheet.append([''])
    summary_start_row = sheet.max_row + 1
    if ficha.peso_final_gramas:
        sheet[f'A{summary_start_row}'] = "Rendimento Estimado:"
        sheet[f'A{summary_start_row}'].font = bold_font
        fatias = ficha.calcular_porcoes(100)
        sheet[f'B{summary_start_row}'] = f'{fatias:.1f} fatias de 100g'.replace('.',',')
    sheet[f'D{summary_start_row}'] = "CUSTO TOTAL:"
    sheet[f'D{summary_start_row}'].font = bold_font
    sheet[f'E{summary_start_row}'] = round(ficha.custo_total(), 2)
    sheet[f'E{summary_start_row}'].font = bold_font
    sheet[f'E{summary_start_row}'].alignment = right_align
    sheet.append(['']); sheet.append([''])
    obs_start_row = sheet.max_row
    sheet[f'A{obs_start_row}'] = "Observações / Modo de Preparo:"
    sheet[f'A{obs_start_row}'].font = bold_font
    sheet.merge_cells(f'A{obs_start_row + 1}:E{obs_start_row + 3}')
    obs_cell = sheet[f'A{obs_start_row + 1}']
    obs_cell.value = ficha.observacoes
    obs_cell.alignment = Alignment(wrap_text=True, vertical='top')
    sheet.column_dimensions['A'].width = 30; sheet.column_dimensions['B'].width = 20
    sheet.column_dimensions['C'].width = 18; sheet.column_dimensions['D'].width = 15
    sheet.column_dimensions['E'].width = 18
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    filename = f"Ficha_Tecnica_{ficha.nome.replace(' ', '_')}.xlsx"
    return Response(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': f'attachment;filename={filename}'})




# Em app.py

@app.route('/ficha-tecnica/produzir/<int:ficha_tecnica_id>', methods=['POST'])
def produzir_ficha_tecnica(ficha_tecnica_id):
    ficha = FichaTecnica.query.get_or_404(ficha_tecnica_id)
    
    # Pega a quantidade a produzir do formulário, padrão é 1
    try:
        quantidade_a_produzir = int(request.form.get('quantidade_a_produzir', 1))
        if quantidade_a_produzir <= 0:
            flash('A quantidade a produzir deve ser maior que zero.', 'warning')
            return redirect(url_for('detalhe_ficha_tecnica', ficha_tecnica_id=ficha_tecnica_id))
    except (ValueError, TypeError):
        flash('Quantidade a produzir inválida.', 'danger')
        return redirect(url_for('detalhe_ficha_tecnica', ficha_tecnica_id=ficha_tecnica_id))

    # 1. VERIFICAÇÃO DE ESTOQUE
    ingredientes_insuficientes = []
    for item in ficha.ingredientes:
        quantidade_necessaria = item.quantidade_usada * quantidade_a_produzir
        if item.ingrediente.quantidade_estoque < quantidade_necessaria:
            ingredientes_insuficientes.append(item.ingrediente.nome)

    # 2. SE HOUVER INGREDIENTES FALTANDO, EXIBE ERRO
    if ingredientes_insuficientes:
        nomes_faltando = ", ".join(ingredientes_insuficientes)
        flash(f'Não foi possível produzir. Estoque insuficiente para: {nomes_faltando}.', 'danger')
        return redirect(url_for('detalhe_ficha_tecnica', ficha_tecnica_id=ficha_tecnica_id))

    # 3. SE HOUVER ESTOQUE, DÁ BAIXA
    for item in ficha.ingredientes:
        quantidade_a_deduzir = item.quantidade_usada * quantidade_a_produzir
        item.ingrediente.quantidade_estoque -= quantidade_a_deduzir
    
    db.session.commit()
    flash(f'{quantidade_a_produzir} unidade(s) de "{ficha.nome}" produzida(s) com sucesso! Estoque atualizado.', 'success')
    return redirect(url_for('detalhe_ficha_tecnica', ficha_tecnica_id=ficha_tecnica_id))

if __name__ == '__main__':
    app.run(debug=True)