
# 🎱 Sistema de Ranking de Sinuca

Sistema completo e funcional para gerenciar ranking de jogadores de sinuca, com registro de partidas MD3, controle de saldo e permissões de acesso.

## 🚀 Funcionalidades

### ✅ Implementadas
- **Cadastro automático** de jogadores na primeira partida
- **Registro de partidas MD3** com opção "dobro ou nada"
- **Cálculo automático** de saldo, aproveitamento e rank (S, A, B, C, D)
- **Histórico completo** de todas as partidas
- **Gráficos visuais** de saldo dos jogadores
- **Sistema de login** com permissões (apenas admin registra partidas)
- **Interface web** responsiva e intuitiva

### 🏆 Sistema de Ranking
- **Rank S:** 85% ou mais de aproveitamento
- **Rank A:** 70% - 84% de aproveitamento  
- **Rank B:** 55% - 69% de aproveitamento
- **Rank C:** 40% - 54% de aproveitamento
- **Rank D:** Abaixo de 40% de aproveitamento

### 💰 Sistema de Valores
- **Partida Normal:** R$ 10 (vencedor +10, perdedor -10)
- **Dobro ou Nada:** R$ 20 (vencedor +20, perdedor -20)

## 🔧 Como Usar

### 1. Executar o Sistema
```bash
python main.py
```
O sistema estará disponível em: `http://0.0.0.0:5000`

### 2. Login de Administrador
- **Usuário:** `admin`
- **Senha:** `admin123`

### 3. Registrar Partidas
1. Faça login como admin
2. Clique em "➕ Registrar Partida"
3. Preencha os nomes dos jogadores
4. Marque o vencedor
5. Opcionalmente, marque "Dobro ou Nada"
6. Confirme o registro

### 4. Visualizar Dados
- **Ranking:** Página principal com todos os jogadores ordenados
- **Histórico:** Lista detalhada de todas as partidas
- **Gráficos:** Visualização do saldo de cada jogador

## 📁 Estrutura do Projeto

```
projeto/
├── main.py                 # Código principal da aplicação Flask
├── jogadores.json          # Banco de dados dos jogadores
├── historico.json          # Histórico das partidas
├── templates/              # Templates HTML
│   ├── base.html          # Template base
│   ├── index.html         # Página principal (ranking)
│   ├── login.html         # Página de login
│   ├── add_partida.html   # Formulário de registro de partida
│   ├── historico.html     # Página de histórico
│   └── graficos.html      # Página de gráficos
└── README.md              # Esta documentação
```

## 🔒 Segurança e Permissões

- **Visualização pública:** Qualquer um pode ver o ranking
- **Funções administrativas:** Apenas usuários logados como admin podem:
  - Registrar novas partidas
  - Ver histórico detalhado
  - Acessar gráficos

## 🛠️ Personalização

### Alterar Credenciais de Admin
No arquivo `main.py`, modifique as linhas:
```python
ADMIN_USER = 'admin'
ADMIN_PASS = 'admin123'
```

### Alterar Valores das Partidas
No arquivo `main.py`, na função `adicionar_partida()`:
```python
# Valor da partida (10 normal, 20 dobro ou nada)
valor = 20 if dobro_nada else 10
```

### Alterar Critérios de Ranking
Na função `calcular_rank()`:
```python
def calcular_rank(aproveitamento):
    if aproveitamento >= 85:    # Rank S
        return 'S'
    elif aproveitamento >= 70:  # Rank A
        return 'A'
    # ... etc
```

## 📊 Dados Persistentes

Os dados são salvos automaticamente em arquivos JSON:

- **jogadores.json:** Estatísticas de cada jogador
- **historico.json:** Registro completo de todas as partidas

### Backup de Dados
Para fazer backup, simplesmente copie os arquivos `.json` para um local seguro.

### Restaurar Dados
Para restaurar, substitua os arquivos `.json` pelos backups salvos.

## 🚀 Expansões Futuras

### Funcionalidades Sugeridas
- [ ] Sistema de torneios
- [ ] Estatísticas avançadas (sequências de vitórias/derrotas)
- [ ] Exportação de relatórios em PDF
- [ ] Sistema de apostas entre jogadores
- [ ] Rankings por período (mensal, anual)
- [ ] Fotos de perfil dos jogadores
- [ ] Sistema de notificações

### Melhorias Técnicas
- [ ] Banco de dados mais robusto (SQLite/PostgreSQL)
- [ ] API REST completa
- [ ] Testes automatizados
- [ ] Deploy automatizado
- [ ] Sistema de logs mais detalhado

## 🐛 Solução de Problemas

### Erro ao Iniciar
- Verifique se todas as dependências estão instaladas
- Certifique-se que a porta 5000 não está sendo usada

### Dados Não Salvam
- Verifique permissões de escrita na pasta do projeto
- Confirme se os arquivos `.json` não estão corrompidos

### Login Não Funciona
- Verifique as credenciais (case-sensitive)
- Limpe o cache do navegador

## 🤝 Contribuições

Este sistema foi desenvolvido para ser facilmente expandível. Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📝 Licença

Este projeto é de uso livre para fins educacionais e pessoais.

---

**Desenvolvido com ❤️ para a comunidade de sinuca!**
