document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('add-block-form');
    const blockchainContainer = document.getElementById('blockchain');
    const refreshButton = document.getElementById('refresh-chain');
    const serverUrl = 'http://localhost:5000'; // URL do servidor 1

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(form);
        const data = {
            cpf: formData.get('cpf'),
            nome: formData.get('nome'),
            naturalidade: formData.get('naturalidade'),
            data_nascimento: formData.get('data_nascimento')
        };

        fetch(`${serverUrl}/add_block`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(block => {
            alert('Bloco adicionado com sucesso!');
            form.reset();
            if (block.nome !== 'Genesis Block') {
                refreshChain();
            } else {
                console.log('Ignorando Genesis Block na interface.');
            }
        })
        .catch(error => {
            console.error('Erro ao adicionar bloco:', error);
            alert('Erro ao adicionar bloco.');
        });
    });

    refreshButton.addEventListener('click', refreshChain);

    function refreshChain() {
        fetch(`${serverUrl}/chain`)
        .then(response => response.json())
        .then(chain => {
            blockchainContainer.innerHTML = ''; // Limpa o conteúdo anterior

            chain.forEach((block, index) => {
                if (block.nome !== 'Genesis Block') {
                    const blockContainer = document.createElement('div');
                    blockContainer.classList.add('block-container');
                    blockContainer.id = `block-${index}`;

                    const blockHeading = document.createElement('h3');
                    blockHeading.textContent = `Bloco ${index + 1}`;
                    blockContainer.appendChild(blockHeading);

                    const cpfElement = document.createElement('p');
                    cpfElement.textContent = `CPF: ${block.cpf}`;
                    cpfElement.id = `cpf-${index}`;
                    blockContainer.appendChild(cpfElement);

                    const nomeElement = document.createElement('p');
                    nomeElement.textContent = `Nome: ${block.nome}`;
                    nomeElement.id = `nome-${index}`;
                    blockContainer.appendChild(nomeElement);

                    const naturalidadeElement = document.createElement('p');
                    naturalidadeElement.textContent = `Naturalidade: ${block.naturalidade}`;
                    naturalidadeElement.id = `naturalidade-${index}`;
                    blockContainer.appendChild(naturalidadeElement);

                    const dataNascimentoElement = document.createElement('p');
                    dataNascimentoElement.textContent = `Data de Nascimento: ${block.data_nascimento}`;
                    dataNascimentoElement.id = `data-nascimento-${index}`;
                    blockContainer.appendChild(dataNascimentoElement);

                    blockchainContainer.appendChild(blockContainer);
                }
            });
        })
        .catch(error => {
            console.error('Erro ao obter a blockchain:', error);
            alert('Erro ao obter a blockchain.');
        });
    }

    // Atualizar a blockchain ao carregar a página
    refreshChain();
});
