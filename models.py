from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

fichatecnica_forma_association = db.Table('fichatecnica_forma',
    db.Column('fichatecnica_id', db.Integer, db.ForeignKey('ficha_tecnica.id'), primary_key=True),
    db.Column('forma_id', db.Integer, db.ForeignKey('forma.id'), primary_key=True)
)

class FichaTecnicaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fichatecnica_id = db.Column(db.Integer, db.ForeignKey('ficha_tecnica.id'), nullable=False)
    ingrediente_id = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable=False)
    quantidade_usada = db.Column(db.Float, nullable=False)
    ingrediente = db.relationship('Ingrediente')

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    marca = db.Column(db.String(100), nullable=True)
    unidade_medida = db.Column(db.String(20), nullable=False) # g, ml, ou unid
    
    # Armazena a quantidade total em estoque na unidade base
    quantidade_estoque = db.Column(db.Float, nullable=False, default=0.0)

    # NOVO CAMPO: Armazena o Custo Médio Ponderado por unidade base
    custo_medio_por_unidade_base = db.Column(db.Float, nullable=False, default=0.0)

    #relacionamento de compra nova.
    compras = db.relationship('Compra', backref='ingrediente', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Ingrediente {self.nome}>'

    def preco_por_unidade(self):
        """Retorna diretamente o custo médio já calculado."""
        return self.custo_medio_por_unidade_base

class FichaTecnica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    rendimento = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    peso_final_gramas = db.Column(db.Float, nullable=True)
    tempo_producao_minutos = db.Column(db.Integer, default=0)
    incluir_custo_mao_de_obra = db.Column(db.Boolean, default=True)

    ingredientes = db.relationship('FichaTecnicaIngrediente', backref='fichatecnica', cascade="all, delete-orphan")
    
    formas = db.relationship('Forma', secondary=fichatecnica_forma_association, lazy='subquery',
        backref=db.backref('fichas_tecnicas', lazy=True))

    # --- MÉTODOS DE CÁLCULO QUE PRECISAM ESTAR AQUI ---
    def custo_ingredientes(self):
        """Calcula apenas o custo dos ingredientes."""
        return sum(item.ingrediente.preco_por_unidade() * item.quantidade_usada for item in self.ingredientes)

    def custo_mao_de_obra(self):
        """Calcula apenas o custo da mão de obra, se aplicável."""
        if self.incluir_custo_mao_de_obra and self.tempo_producao_minutos and self.tempo_producao_minutos > 0:
            config = Configuracao.query.get(1)
            if config and config.custo_hora_calculado > 0:
                custo_por_minuto = config.custo_hora_calculado / 60
                return self.tempo_producao_minutos * custo_por_minuto
        return 0

    def custo_total(self):
        """Soma o custo dos ingredientes com o da mão de obra."""
        return self.custo_ingredientes() + self.custo_mao_de_obra()

    def calcular_porcoes(self, gramas_por_porcao=100.0):
        if self.peso_final_gramas and gramas_por_porcao > 0:
            return self.peso_final_gramas / gramas_por_porcao
        return 0

class Forma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), unique=True, nullable=False)



# Em models.py, adicione esta classe ao final

class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Usaremos sempre o id=1
    custo_gas = db.Column(db.Float, default=0.0)
    custo_luz = db.Column(db.Float, default=0.0)
    custo_agua = db.Column(db.Float, default=0.0)
    custo_outros = db.Column(db.Float, default=0.0)
    salario_desejado = db.Column(db.Float, default=0.0)
    horas_por_dia = db.Column(db.Float, default=8.0)
    dias_por_semana = db.Column(db.Integer, default=5)
    
    # Campo para armazenar o resultado do cálculo
    custo_hora_calculado = db.Column(db.Float, default=0.0)

    def calcular_custo_hora(self):
        """Calcula e atualiza o custo da hora de trabalho."""
        custos_totais_mensais = (self.custo_gas or 0) + \
                               (self.custo_luz or 0) + \
                               (self.custo_agua or 0) + \
                               (self.custo_outros or 0) + \
                               (self.salario_desejado or 0)
        
        horas_trabalhadas_mes = (self.horas_por_dia or 0) * \
                                (self.dias_por_semana or 0) * 4.33 # Média de semanas no mês
        
        if horas_trabalhadas_mes > 0:
            self.custo_hora_calculado = custos_totais_mensais / horas_trabalhadas_mes
        else:
            self.custo_hora_calculado = 0
        
        return self.custo_hora_calculado
    

    #Informação sobre a compra nova e o registro da compra antiga.

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_compra = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    preco_total_lote = db.Column(db.Float, nullable=False)
    unidades_compradas = db.Column(db.Integer, nullable=False)
    tamanho_unidade = db.Column(db.Float, nullable=False)

    ingrediente_id = db.Column(db.Integer, db.ForeignKey('ingrediente.id'), nullable=False)

    def custo_unitario_base(self):
        total_comprado = self.tamanho_unidade * self.unidades_compradas
        if total_comprado > 0:
            return self.preco_total_lote / total_comprado
        return 0
    
