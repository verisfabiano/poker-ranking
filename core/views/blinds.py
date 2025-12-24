from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db import transaction
from ..models import BlindStructure, BlindLevel
from .auth import admin_required
from .ranking import tenant_required

@admin_required
def blind_structures_list(request):
    if not request.tenant:
        return redirect("login")
    
    structures = BlindStructure.objects.filter(tenant=request.tenant).order_by("nome")
    return render(request, "blind_structures_list.html", {"structures": structures})

@admin_required
def blind_structure_create(request):
    if not request.tenant:
        return redirect("login")
    
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        descricao = request.POST.get("descricao", "").strip()
        
        if nome:
            s = BlindStructure.objects.create(
                nome=nome, 
                descricao=descricao,
                tenant=request.tenant
            )
            # Redireciona para a tela de gerenciar níveis dessa estrutura
            return redirect(reverse("blind_structure_manage", args=[s.id]))
    
    # Mostrar templates prontos (sem tenant) para clonagem
    templates = BlindStructure.objects.filter(tenant__isnull=True).order_by("nome")
    return render(request, "blind_structure_form.html", {"structure": None, "templates": templates})

@admin_required
def clone_blind_structure(request, template_id):
    """
    Clona um template de estrutura de blinds para o tenant do usuário.
    """
    if not request.tenant:
        return redirect("login")
    
    template = get_object_or_404(BlindStructure, id=template_id, tenant__isnull=True)
    
    with transaction.atomic():
        # Criar nova estrutura para este tenant
        new_structure = BlindStructure.objects.create(
            nome=template.nome,
            descricao=template.descricao,
            tenant=request.tenant
        )
        
        # Clonar todos os níveis
        for level in template.levels.all():
            BlindLevel.objects.create(
                structure=new_structure,
                tenant=request.tenant,
                ordem=level.ordem,
                small_blind=level.small_blind,
                big_blind=level.big_blind,
                ante=level.ante,
                tempo_minutos=level.tempo_minutos,
                is_break=level.is_break
            )
    
    return redirect(reverse("blind_structure_manage", args=[new_structure.id]))

@admin_required
def blind_structure_manage(request, structure_id):
    """
    Tela principal onde adicionamos/editamos níveis de uma estrutura.
    """
    if not request.tenant:
        return redirect("login")
    
    structure = get_object_or_404(BlindStructure, id=structure_id, tenant=request.tenant)
    
    if request.method == "POST":
        # Ação de ADICIONAR NÍVEL
        if "add_level" in request.POST:
            sb = request.POST.get("small_blind", "0")
            bb = request.POST.get("big_blind", "0")
            ante = request.POST.get("ante", "0")
            tempo = request.POST.get("tempo", "20")
            is_break = request.POST.get("is_break") == "on"
            
            # Descobrir a próxima ordem (última + 1)
            last_level = structure.levels.last()
            next_order = (last_level.ordem + 1) if last_level else 1
            
            BlindLevel.objects.create(
                structure=structure,
                tenant=request.tenant,
                ordem=next_order,
                small_blind=int(sb) if sb else 0,
                big_blind=int(bb) if bb else 0,
                ante=int(ante) if ante else 0,
                tempo_minutos=int(tempo) if tempo else 20,
                is_break=is_break
            )
            return redirect(reverse("blind_structure_manage", args=[structure.id]))

        # Ação de EDITAR NÍVEL
        if "edit_level" in request.POST:
            level_id = request.POST.get("level_id")
            level = BlindLevel.objects.filter(id=level_id, structure=structure).first()
            
            if level:
                sb = request.POST.get("small_blind", "0")
                bb = request.POST.get("big_blind", "0")
                ante = request.POST.get("ante", "0")
                tempo = request.POST.get("tempo", "20")
                is_break = request.POST.get("is_break") == "on"
                
                level.small_blind = int(sb) if sb else 0
                level.big_blind = int(bb) if bb else 0
                level.ante = int(ante) if ante else 0
                level.tempo_minutos = int(tempo) if tempo else 20
                level.is_break = is_break
                level.save()
            
            return redirect(reverse("blind_structure_manage", args=[structure.id]))

        # Ação de EXCLUIR NÍVEL
        if "delete_level" in request.POST:
            level_id = request.POST.get("level_id")
            BlindLevel.objects.filter(id=level_id, structure=structure).delete()
            # Reordenar os níveis restantes
            levels = structure.levels.all()
            for i, lvl in enumerate(levels, start=1):
                lvl.ordem = i
                lvl.save()
            return redirect(reverse("blind_structure_manage", args=[structure.id]))

    levels = structure.levels.all()
    return render(request, "blind_structure_manage.html", {"structure": structure, "levels": levels})