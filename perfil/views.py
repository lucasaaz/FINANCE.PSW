from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
from extrato.models import Valores
from datetime import datetime
from .utils import calcula_total, calcula_equilibrio_financeiro
from contas.models import ContaPaga, ContaPagar

# Create your views here.
def home(request):
    contas = Conta.objects.all()

    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')

    # total_contas = 0
    # for i in contas:
    #     total_contas += i.valor
    total_contas = calcula_total(contas, 'valor')

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    contas2 = ContaPagar.objects.all()
    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')
    contas_vencidas = contas2.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    num_contas_vencidas = 0
    for i in contas_vencidas:
        num_contas_vencidas += 1
    contas_proximas_vencimento = contas2.filter(dia_pagamento__lte = DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    num_contas_proximas_vencimento = 0
    for i in contas_proximas_vencimento:
        num_contas_proximas_vencimento += 1

    return render(request, 'home.html', {'contas': contas, 
                                         'total_contas': total_contas, 
                                         'total_entradas': total_entradas, 
                                         'total_saidas': total_saidas, 
                                         'percentual_gastos_essenciais': int(percentual_gastos_essenciais), 
                                         'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais),
                                         'num_contas_vencidas': num_contas_vencidas,
                                         'num_contas_proximas_vencimento': num_contas_proximas_vencimento})

def gerenciar(request):
    categorias = Categoria.objects.all()
    contas = Conta.objects.all()

    total_contas = 0
    for i in contas:
        total_contas += i.valor

    return render(request, 'gerenciar.html', {'contas': contas, 'total_contas': total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if apelido.strip() == "" or valor.strip() == "":
        messages.add_message(request, constants.ERROR, "Preencha todos os campos !!")
        return redirect('/perfil/gerenciar')

    conta = Conta(
        apelido=apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()

    messages.add_message(request, constants.SUCCESS, "Conta cadastrada com sucesso !!")

    return redirect('/perfil/gerenciar')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, "Conta deletada com sucesso !!")

    return redirect('/perfil/gerenciar')

def cadastrar_categoria(request):
    categoria = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    if categoria.strip() == "":
        messages.add_message(request, constants.ERROR, "Preencha todos os campos !!")
        return redirect('/perfil/gerenciar')

    categoria = Categoria(
        categoria = categoria,
        essencial = essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, "Categoria adicionada com sucesso !!")

    return redirect('/perfil/gerenciar')

def trocar_essencial(request, id):
    categorias = Categoria.objects.get(id=id)

    categorias.essencial = not categorias.essencial

    categorias.save()

    messages.add_message(request, constants.SUCCESS, "Categoria essencial trocada com sucesso !!")

    return redirect('/perfil/gerenciar')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total += v.valor
        dados[categoria.categoria] = total

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})

