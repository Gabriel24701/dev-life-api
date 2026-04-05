# Usa uma imagem Node
FROM node:20-alpine

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração de dependências
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o resto do código
COPY . .

# Faz o build de produção do Next.js
RUN npx next build --webpack

# Expõe a porta que o Next usa
EXPOSE 3000

# Comando para iniciar o servidor
CMD ["npm", "start"]