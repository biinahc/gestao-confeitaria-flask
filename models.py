from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Tabela de associação para o relacionamento Muitos-para-Muitos
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
    unidade_medida = db.Column(db.String(20), nullable=False)
    quantidade_estoque = db.Column(db.Float, nullable=False, default=0.0)
    custo_medio_por_unidade_base = db.Column(db.Float, nullable=False, default=0.0)
    compras = db.relationship('Compra', backref='ingrediente', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Ingrediente {self.nome}>'

    def preco_por_unidade(self):
        return self.custo_medio_por_unidade_base

class FichaTecnica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    rendimento = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    peso_final_gramas = db.Column(db.Float, nullable=True)
    tempo_producao_horas = db.Column(db.Integer, default=0)
    tempo_producao_minutos = db.Column(db.Integer, default=0)
    incluir_custo_mao_de_obra = db.Column(db.Boolean, default=True)
    ingredientes = db.relationship('FichaTecnicaIngrediente', backref='fichatecnica', cascade="all, delete-orphan")
    formas = db.relationship('Forma', secondary=fichatecnica_forma_association, lazy='subquery',
        backref=db.backref('fichas_tecnicas', lazy=True))
    vendas = db.relationship('Venda', backref='ficha_tecnica', lazy=True)

    def custo_ingredientes(self):
        return sum(item.ingrediente.preco_por_unidade() * item.quantidade_usada for item in self.ingredientes)

    def custo_mao_de_obra(self):
        tempo_total_minutos = ((self.tempo_producao_horas or 0) * 60) + (self.tempo_producao_minutos or 0)
        if self.incluir_custo_mao_de_obra and tempo_total_minutos > 0:
            config = Configuracao.query.get(1)
            if config and config.custo_hora_calculado > 0:
                custo_por_minuto = config.custo_hora_calculado / 60
                return tempo_total_minutos * custo_por_minuto
        return 0

    def custo_total(self):
        return self.custo_ingredientes() + self.custo_mao_de_obra()

    def calcular_porcoes(self, gramas_por_porcao=100.0):
        if self.peso_final_gramas and gramas_por_porcao > 0:
            return self.peso_final_gramas / gramas_por_porcao
        return 0

class Forma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), unique=True, nullable=False)

class Configuracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custo_gas = db.Column(db.Float, default=0.0)
    custo_luz = db.Column(db.Float, default=0.0)
    custo_agua = db.Column(db.Float, default=0.0)
    custo_outros = db.Column(db.Float, default=0.0)
    salario_desejado = db.Column(db.Float, default=0.0)
    horas_por_dia = db.Column(db.Float, default=8.0)
    dias_por_semana = db.Column(db.Integer, default=5)
    custo_hora_calculado = db.Column(db.Float, default=0.0)

    def calcular_custo_hora(self):
        custos_totais_mensais = (self.custo_gas or 0) + (self.custo_luz or 0) + \
                               (self.custo_agua or 0) + (self.custo_outros or 0) + \
                               (self.salario_desejado or 0)
        horas_trabalhadas_mes = (self.horas_por_dia or 0) * (self.dias_por_semana or 0) * 4.33
        if horas_trabalhadas_mes > 0:
            self.custo_hora_calculado = custos_totais_mensais / horas_trabalhadas_mes
        else:
            self.custo_hora_calculado = 0
        return self.custo_hora_calculado
    
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
    
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_venda = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_venda_final = db.Column(db.Float, nullable=False)
    custo_producao_total = db.Column(db.Float, nullable=False)
    lucro_calculado = db.Column(db.Float, nullable=False)
    fichatecnica_id = db.Column(db.Integer, db.ForeignKey('ficha_tecnica.id'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)