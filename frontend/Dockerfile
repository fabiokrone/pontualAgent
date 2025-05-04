FROM node:18-alpine

WORKDIR /app

# Instala as dependências necessárias
RUN apk add --no-cache git python3 make g++

# Copia os arquivos de pacote
COPY package.json package-lock.json ./

# Limpa instalações anteriores
RUN rm -rf node_modules .next
RUN npm cache clean --force

# Instala dependências
RUN npm install

# Copia o restante da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p .next
RUN echo "{}" > .next/fallback-build-manifest.json

# Define variáveis de ambiente
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=development

# Expõe a porta
EXPOSE 3000

# Executa em modo de desenvolvimento
CMD ["npm", "run", "dev", "--", "--port", "3000", "--hostname", "0.0.0.0"]