
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'sinuca_ranking_secret_key_2025'

# Configuração de arquivos de dados
JOGADORES_FILE = 'jogadores.json'
HISTORICO_FILE = 'historico.json'
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'

def carregar_dados(arquivo):
    """Carrega dados de um arquivo JSON"""
    if os.path.exists(arquivo):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_dados(dados, arquivo):
    """Salva dados em um arquivo JSON"""
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def calcular_rank(aproveitamento):
    """Calcula o rank baseado no aproveitamento (usado apenas como sugestão)"""
    if aproveitamento >= 85:
        return 'S'
    elif aproveitamento >= 70:
        return 'A'
    elif aproveitamento >= 55:
        return 'B'
    elif aproveitamento >= 40:
        return 'C'
    else:
        return 'D'

def atualizar_estatisticas_jogador(nome, vitoria, valor):
    """Atualiza as estatísticas de um jogador"""
    jogadores = carregar_dados(JOGADORES_FILE)
    
    if nome not in jogadores:
        jogadores[nome] = {
            'vitorias': 0,
            'derrotas': 0,
            'saldo': 0,
            'aproveitamento': 0,
            'rank': 'D'
        }
    
    if vitoria:
        jogadores[nome]['vitorias'] += 1
        jogadores[nome]['saldo'] += valor
    else:
        jogadores[nome]['derrotas'] += 1
        jogadores[nome]['saldo'] -= valor
    
    total_jogos = jogadores[nome]['vitorias'] + jogadores[nome]['derrotas']
    if total_jogos > 0:
        jogadores[nome]['aproveitamento'] = round((jogadores[nome]['vitorias'] / total_jogos) * 100, 1)
    
    # Não atualizar rank automaticamente - apenas manter o atual ou sugerir
    if 'rank' not in jogadores[nome]:
        jogadores[nome]['rank'] = calcular_rank(jogadores[nome]['aproveitamento'])
    
    salvar_dados(jogadores, JOGADORES_FILE)

@app.route('/')
def home():
    """Página principal com ranking"""
    jogadores = carregar_dados(JOGADORES_FILE)
    
    # Ordenar por rank e depois por saldo
    rank_order = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
    jogadores_ordenados = dict(sorted(
        jogadores.items(), 
        key=lambda x: (rank_order.get(x[1]['rank'], 0), x[1]['saldo']), 
        reverse=True
    ))
    
    return render_template('index.html', jogadores=jogadores_ordenados, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Sistema de login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['user'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do sistema"""
    session.pop('user', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('home'))

@app.route('/editar_jogador/<nome>', methods=['GET', 'POST'])
def editar_jogador(nome):
    """Editar informações do jogador (apenas admin)"""
    if 'user' not in session or session['user'] != ADMIN_USER:
        flash('Acesso negado! Apenas admin pode editar jogadores.', 'error')
        return redirect(url_for('home'))
    
    jogadores = carregar_dados(JOGADORES_FILE)
    
    if nome not in jogadores:
        flash('Jogador não encontrado!', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        novo_rank = request.form['rank']
        if novo_rank in ['S', 'A', 'B', 'C', 'D']:
            jogadores[nome]['rank'] = novo_rank
            salvar_dados(jogadores, JOGADORES_FILE)
            flash(f'Rank de {nome} atualizado para {novo_rank}!', 'success')
        else:
            flash('Rank inválido!', 'error')
        
        return redirect(url_for('home'))
    
    return render_template('editar_jogador.html', nome=nome, jogador=jogadores[nome])

@app.route('/add', methods=['GET', 'POST'])
def adicionar_partida():
    """Adicionar nova partida (apenas admin)"""
    if 'user' not in session or session['user'] != ADMIN_USER:
        flash('Acesso negado! Apenas admin pode registrar partidas.', 'error')
        return redirect(url_for('home'))
    
    jogadores = carregar_dados(JOGADORES_FILE)
    
    if request.method == 'POST':
        jogador1 = request.form['jogador1']
        jogador2 = request.form['jogador2']
        vencedor_p1 = request.form['vencedor_partida1']
        vencedor_p2 = request.form['vencedor_partida2']
        vencedor_p3 = request.form.get('vencedor_partida3', 'nao_jogada')
        dobro_nada = 'dobro_nada' in request.form
        
        if not jogador1 or not jogador2:
            flash('Por favor, selecione ambos os jogadores!', 'error')
            return render_template('add_partida.html', jogadores=jogadores)
        
        if jogador1 == jogador2:
            flash('Os jogadores devem ser diferentes!', 'error')
            return render_template('add_partida.html', jogadores=jogadores)
        
        # Calcular placar MD3
        vitorias_j1 = 0
        vitorias_j2 = 0
        
        if vencedor_p1 == 'jogador1':
            vitorias_j1 += 1
        else:
            vitorias_j2 += 1
            
        if vencedor_p2 == 'jogador1':
            vitorias_j1 += 1
        else:
            vitorias_j2 += 1
        
        # Se não houve partida 3, definir vencedor
        if vencedor_p3 == 'nao_jogada':
            if vitorias_j1 == 2:
                nome_vencedor = jogador1
                placar = "2-0"
            elif vitorias_j2 == 2:
                nome_vencedor = jogador2
                placar = "2-0"
            else:
                flash('Erro: Se não houve terceira partida, alguém deve ter vencido 2-0!', 'error')
                return render_template('add_partida.html', jogadores=jogadores)
        else:
            # Houve partida 3
            if vencedor_p3 == 'jogador1':
                vitorias_j1 += 1
            else:
                vitorias_j2 += 1
            
            if vitorias_j1 == 2:
                nome_vencedor = jogador1
                placar = "2-1"
            elif vitorias_j2 == 2:
                nome_vencedor = jogador2
                placar = "2-1"
            else:
                flash('Erro: Placar inválido para MD3!', 'error')
                return render_template('add_partida.html', jogadores=jogadores)
        
        # Valor da partida (10 normal, 20 dobro ou nada)
        valor = 20 if dobro_nada else 10
        
        # Atualizar estatísticas
        if nome_vencedor == jogador1:
            atualizar_estatisticas_jogador(jogador1, True, valor)
            atualizar_estatisticas_jogador(jogador2, False, valor)
        else:
            atualizar_estatisticas_jogador(jogador1, False, valor)
            atualizar_estatisticas_jogador(jogador2, True, valor)
        
        # Salvar no histórico
        historico = carregar_dados(HISTORICO_FILE)
        if 'partidas' not in historico:
            historico['partidas'] = []
        
        partida = {
            'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'jogador1': jogador1,
            'jogador2': jogador2,
            'vencedor': nome_vencedor,
            'placar': placar,
            'valor': valor,
            'dobro_nada': dobro_nada,
            'tipo': 'Dobro ou Nada' if dobro_nada else 'Normal'
        }
        
        historico['partidas'].insert(0, partida)  # Mais recente primeiro
        salvar_dados(historico, HISTORICO_FILE)
        
        flash(f'Partida registrada com sucesso! {nome_vencedor} venceu por {placar}!', 'success')
        return redirect(url_for('home'))
    
    return render_template('add_partida.html', jogadores=jogadores)

@app.route('/historico')
def historico():
    """Visualizar histórico de partidas"""
    historico_data = carregar_dados(HISTORICO_FILE)
    partidas = historico_data.get('partidas', [])
    
    return render_template('historico.html', partidas=partidas)

@app.route('/graficos')
def graficos():
    """Página de gráficos"""
    jogadores = carregar_dados(JOGADORES_FILE)
    return render_template('graficos.html', jogadores=jogadores)

@app.route('/perfil/<nome>')
def perfil_jogador(nome):
    """Página de perfil detalhado do jogador"""
    jogadores = carregar_dados(JOGADORES_FILE)
    historico_data = carregar_dados(HISTORICO_FILE)
    
    if nome not in jogadores:
        flash('Jogador não encontrado!', 'error')
        return redirect(url_for('home'))
    
    jogador = jogadores[nome]
    partidas_todas = historico_data.get('partidas', [])
    
    # Filtrar partidas do jogador
    partidas_jogador = []
    estatisticas_oponentes = {}
    
    for partida in partidas_todas:
        if partida['jogador1'] == nome or partida['jogador2'] == nome:
            # Determinar oponente e resultado
            if partida['jogador1'] == nome:
                oponente = partida['jogador2']
                vitoria = partida['vencedor'] == nome
                placar = partida.get('placar', '2-0')  # Usar placar real se disponível
            else:
                oponente = partida['jogador1']
                vitoria = partida['vencedor'] == nome
                placar = partida.get('placar', '2-0')  # Usar placar real se disponível
            
            # Se perdeu, inverter placar
            if not vitoria:
                if placar == "2-0":
                    placar = "0-2"
                elif placar == "2-1":
                    placar = "1-2"
            
            partidas_jogador.append({
                'data': partida['data'],
                'oponente': oponente,
                'vitoria': vitoria,
                'placar': placar,
                'dobro_nada': partida.get('dobro_nada', False),
                'valor': partida['valor']
            })
            
            # Estatísticas contra oponentes
            if oponente not in estatisticas_oponentes:
                estatisticas_oponentes[oponente] = {
                    'vitorias': 0,
                    'derrotas': 0,
                    'total': 0
                }
            
            if vitoria:
                estatisticas_oponentes[oponente]['vitorias'] += 1
            else:
                estatisticas_oponentes[oponente]['derrotas'] += 1
            estatisticas_oponentes[oponente]['total'] += 1
    
    # Calcular aproveitamento contra cada oponente
    estatisticas_detalhadas = {}
    for oponente, stats in estatisticas_oponentes.items():
        aproveitamento = round((stats['vitorias'] / stats['total']) * 100, 1) if stats['total'] > 0 else 0
        estatisticas_detalhadas[oponente] = {
            'vitorias': stats['vitorias'],
            'derrotas': stats['derrotas'],
            'total': stats['total'],
            'aproveitamento': aproveitamento
        }
    
    # Encontrar freguês (quem mais perdeu para este jogador) e arqui-inimigo (quem mais ganhou deste jogador)
    fregues = None
    arqui_inimigo = None
    
    if estatisticas_oponentes:
        # Freguês: oponente com mais derrotas (e pelo menos 3 jogos)
        candidatos_fregues = [(oponente, stats) for oponente, stats in estatisticas_oponentes.items() 
                              if stats['total'] >= 3 and stats['vitorias'] > stats['derrotas']]
        if candidatos_fregues:
            oponente_fregues, stats_fregues = max(candidatos_fregues, key=lambda x: x[1]['vitorias'])
            fregues = {
                'nome': oponente_fregues,
                'vitorias_contra': stats_fregues['vitorias'],
                'derrotas_contra': stats_fregues['derrotas']
            }
        
        # Arqui-inimigo: oponente com mais vitórias contra este jogador (e pelo menos 3 jogos)
        candidatos_inimigo = [(oponente, stats) for oponente, stats in estatisticas_oponentes.items() 
                              if stats['total'] >= 3 and stats['derrotas'] > stats['vitorias']]
        if candidatos_inimigo:
            oponente_inimigo, stats_inimigo = max(candidatos_inimigo, key=lambda x: x[1]['derrotas'])
            arqui_inimigo = {
                'nome': oponente_inimigo,
                'vitorias_contra': stats_inimigo['vitorias'],
                'derrotas_contra': stats_inimigo['derrotas']
            }
    
    return render_template('perfil_jogador.html', 
                         nome=nome, 
                         jogador=jogador,
                         partidas_jogador=partidas_jogador,
                         estatisticas_detalhadas=estatisticas_detalhadas,
                         estatisticas_oponentes={
                             'fregues': fregues,
                             'arqui_inimigo': arqui_inimigo
                         })

@app.route('/editar_partida/<int:index>', methods=['GET', 'POST'])
def editar_partida(index):
    """Editar uma partida específica (apenas admin)"""
    if 'user' not in session or session['user'] != ADMIN_USER:
        flash('Acesso negado! Apenas admin pode editar partidas.', 'error')
        return redirect(url_for('home'))
    
    historico_data = carregar_dados(HISTORICO_FILE)
    partidas = historico_data.get('partidas', [])
    
    if index >= len(partidas) or index < 0:
        flash('Partida não encontrada!', 'error')
        return redirect(url_for('historico'))
    
    partida = partidas[index]
    jogadores = carregar_dados(JOGADORES_FILE)
    
    if request.method == 'POST':
        # Reverter estatísticas da partida original
        jogador1_original = partida['jogador1']
        jogador2_original = partida['jogador2']
        vencedor_original = partida['vencedor']
        valor_original = partida['valor']
        
        # Reverter saldo e estatísticas
        if vencedor_original == jogador1_original:
            jogadores[jogador1_original]['vitorias'] -= 1
            jogadores[jogador1_original]['saldo'] -= valor_original
            jogadores[jogador2_original]['derrotas'] -= 1
            jogadores[jogador2_original]['saldo'] += valor_original
        else:
            jogadores[jogador1_original]['derrotas'] -= 1
            jogadores[jogador1_original]['saldo'] += valor_original
            jogadores[jogador2_original]['vitorias'] -= 1
            jogadores[jogador2_original]['saldo'] -= valor_original
        
        # Recalcular aproveitamento
        for jogador in [jogador1_original, jogador2_original]:
            total_jogos = jogadores[jogador]['vitorias'] + jogadores[jogador]['derrotas']
            if total_jogos > 0:
                jogadores[jogador]['aproveitamento'] = round((jogadores[jogador]['vitorias'] / total_jogos) * 100, 1)
            else:
                jogadores[jogador]['aproveitamento'] = 0
        
        # Obter novos dados
        novo_jogador1 = request.form['jogador1']
        novo_jogador2 = request.form['jogador2']
        vencedor_p1 = request.form['vencedor_partida1']
        vencedor_p2 = request.form['vencedor_partida2']
        vencedor_p3 = request.form.get('vencedor_partida3', 'nao_jogada')
        dobro_nada = 'dobro_nada' in request.form
        
        # Calcular novo placar
        vitorias_j1 = 0
        vitorias_j2 = 0
        
        if vencedor_p1 == 'jogador1':
            vitorias_j1 += 1
        else:
            vitorias_j2 += 1
            
        if vencedor_p2 == 'jogador1':
            vitorias_j1 += 1
        else:
            vitorias_j2 += 1
        
        if vencedor_p3 == 'nao_jogada':
            if vitorias_j1 == 2:
                novo_vencedor = novo_jogador1
                placar = "2-0"
            elif vitorias_j2 == 2:
                novo_vencedor = novo_jogador2
                placar = "2-0"
            else:
                flash('Erro: Se não houve terceira partida, alguém deve ter vencido 2-0!', 'error')
                return render_template('editar_partida.html', partida=partida, jogadores=jogadores, index=index)
        else:
            if vencedor_p3 == 'jogador1':
                vitorias_j1 += 1
            else:
                vitorias_j2 += 1
            
            if vitorias_j1 == 2:
                novo_vencedor = novo_jogador1
                placar = "2-1"
            elif vitorias_j2 == 2:
                novo_vencedor = novo_jogador2
                placar = "2-1"
            else:
                flash('Erro: Placar inválido para MD3!', 'error')
                return render_template('editar_partida.html', partida=partida, jogadores=jogadores, index=index)
        
        novo_valor = 20 if dobro_nada else 10
        
        # Aplicar novas estatísticas
        if novo_vencedor == novo_jogador1:
            atualizar_estatisticas_jogador(novo_jogador1, True, novo_valor)
            atualizar_estatisticas_jogador(novo_jogador2, False, novo_valor)
        else:
            atualizar_estatisticas_jogador(novo_jogador1, False, novo_valor)
            atualizar_estatisticas_jogador(novo_jogador2, True, novo_valor)
        
        # Atualizar partida no histórico
        partidas[index] = {
            'data': partida['data'],  # Manter data original
            'jogador1': novo_jogador1,
            'jogador2': novo_jogador2,
            'vencedor': novo_vencedor,
            'placar': placar,
            'valor': novo_valor,
            'dobro_nada': dobro_nada,
            'tipo': 'Dobro ou Nada' if dobro_nada else 'Normal'
        }
        
        historico_data['partidas'] = partidas
        salvar_dados(historico_data, HISTORICO_FILE)
        
        flash('Partida editada com sucesso!', 'success')
        return redirect(url_for('historico'))
    
    return render_template('editar_partida.html', partida=partida, jogadores=jogadores, index=index)

@app.route('/excluir_partida/<int:index>', methods=['POST'])
def excluir_partida(index):
    """Excluir uma partida específica (apenas admin)"""
    if 'user' not in session or session['user'] != ADMIN_USER:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    historico_data = carregar_dados(HISTORICO_FILE)
    partidas = historico_data.get('partidas', [])
    
    if index >= len(partidas) or index < 0:
        return jsonify({'success': False, 'message': 'Partida não encontrada'})
    
    partida = partidas[index]
    jogadores = carregar_dados(JOGADORES_FILE)
    
    # Reverter estatísticas da partida
    jogador1 = partida['jogador1']
    jogador2 = partida['jogador2']
    vencedor = partida['vencedor']
    valor = partida['valor']
    
    if vencedor == jogador1:
        jogadores[jogador1]['vitorias'] -= 1
        jogadores[jogador1]['saldo'] -= valor
        jogadores[jogador2]['derrotas'] -= 1
        jogadores[jogador2]['saldo'] += valor
    else:
        jogadores[jogador1]['derrotas'] -= 1
        jogadores[jogador1]['saldo'] += valor
        jogadores[jogador2]['vitorias'] -= 1
        jogadores[jogador2]['saldo'] -= valor
    
    # Recalcular aproveitamento
    for jogador in [jogador1, jogador2]:
        total_jogos = jogadores[jogador]['vitorias'] + jogadores[jogador]['derrotas']
        if total_jogos > 0:
            jogadores[jogador]['aproveitamento'] = round((jogadores[jogador]['vitorias'] / total_jogos) * 100, 1)
        else:
            jogadores[jogador]['aproveitamento'] = 0
    
    # Remover partida do histórico
    partidas.pop(index)
    historico_data['partidas'] = partidas
    
    # Salvar dados atualizados
    salvar_dados(jogadores, JOGADORES_FILE)
    salvar_dados(historico_data, HISTORICO_FILE)
    
    return jsonify({'success': True})

@app.route('/api/dados-graficos')
def api_dados_graficos():
    """API para dados dos gráficos"""
    jogadores = carregar_dados(JOGADORES_FILE)
    
    nomes = list(jogadores.keys())
    saldos = [jogadores[nome]['saldo'] for nome in nomes]
    
    return jsonify({
        'nomes': nomes,
        'saldos': saldos
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
@app.route('/editar_jogador/<nome>', methods=['GET', 'POST'])
def editar_jogador(nome):
    """Editar informações do jogador (apenas admin)"""
    if 'user' not in session or session['user'] != ADMIN_USER:
        flash('Acesso negado! Apenas admin pode editar jogadores.', 'error')
        return redirect(url_for('home'))

    jogadores = carregar_dados(JOGADORES_FILE)

    if nome not in jogadores:
        flash('Jogador não encontrado!', 'error')
        return redirect(url_for('home'))

    if request.method == 'POST':
        novo_nome = request.form['nome']
        nova_imagem = request.form['imagem']
        novo_rank = request.form['rank']

        if novo_rank in ['S', 'A', 'B', 'C', 'D']:
            jogadores[nome]['rank'] = novo_rank
            jogadores[nome]['imagem'] = nova_imagem  # Atualizar imagem
            if novo_nome != nome:
                jogadores[nome]['nome'] = novo_nome  # Atualizar nome
                jogadores[novo_nome] = jogadores.pop(nome)  # Mover dados para o novo nome
            salvar_dados(jogadores, JOGADORES_FILE)
            flash(f'Informações de {novo_nome} atualizadas!', 'success')
        else:
            flash('Rank inválido!', 'error')

        return redirect(url_for('home'))

    return render_template('editar_jogador.html', nome=nome, jogador=jogadores[nome])