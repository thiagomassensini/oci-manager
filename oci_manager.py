#!/usr/bin/env python3
"""
OCI Manager v4.0 - Sistema Completo Otimizado
Author: Thiago Massensini
"""

import os
import sys
import json
import time
import ipaddress
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
from typing import Dict, List, Optional

# Tentar importar bibliotecas
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.progress import Progress, track
    from rich.columns import Columns
    from rich.text import Text
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich não disponível. Usando interface básica.")

try:
    import oci
    from oci.config import from_file
    OCI_AVAILABLE = True
except ImportError:
    OCI_AVAILABLE = False
    print("OCI SDK não disponível. Algumas funcionalidades estarão limitadas.")

# Console (compatível com ou sem rich)
if RICH_AVAILABLE:
    console = Console()
else:
    class SimpleConsole:
        def print(self, *args, **kwargs):
            print(*args)
        def clear(self):
            os.system('clear')
    console = SimpleConsole()

class OCIManager:
    """Gerenciador Principal OCI v4.0"""
    
    def __init__(self):
        self.version = "4.0"
        self.config_file = Path.home() / ".oci" / "config"
        self.reports_dir = Path(__file__).parent / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile = None
        self.config = None
        self.clients = {}
        
    def show_banner(self):
        """Exibe banner principal"""
        if RICH_AVAILABLE:
            console.clear()
        else:
            os.system('clear')
            
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        ██████╗  ██████╗██╗    ███╗   ███╗ ██████╗ ██████╗      ║
║       ██╔═══██╗██╔════╝██║    ████╗ ████║██╔════╝ ██╔══██╗     ║
║       ██║   ██║██║     ██║    ██╔████╔██║██║  ███╗██████╔╝     ║
║       ██║   ██║██║     ██║    ██║╚██╔╝██║██║   ██║██╔══██╗     ║
║       ╚██████╔╝╚██████╗██║    ██║ ╚═╝ ██║╚██████╔╝██║  ██║     ║
║        ╚═════╝  ╚═════╝╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝     ║
║                                                                  ║
║              Oracle Cloud Infrastructure Manager v4.0            ║
║                     By: Thiago Massensini                       ║
╚══════════════════════════════════════════════════════════════════╗
        """
        
        if RICH_AVAILABLE:
            console.print(banner, style="bold cyan")
        else:
            print(banner)
        
    def select_profile(self):
        """Seleciona profile OCI"""
        profiles = ["DEFAULT", "INANNA", "HERICKASF"]
        
        console.print("\n📁 Profiles disponíveis:", style="bold yellow" if RICH_AVAILABLE else None)
        for i, profile in enumerate(profiles, 1):
            console.print(f"  {i}) {profile}", style="cyan" if RICH_AVAILABLE else None)
        
        if RICH_AVAILABLE:
            choice = Prompt.ask("Selecione o profile", choices=["1", "2", "3"])
        else:
            choice = input("Selecione o profile (1/2/3): ")
            
        self.current_profile = profiles[int(choice) - 1]
        
        if not OCI_AVAILABLE:
            console.print("⚠️  OCI SDK não disponível. Funcionalidades limitadas.", style="yellow" if RICH_AVAILABLE else None)
            return True
        
        # Carregar configuração
        try:
            self.config = from_file(
                file_location=str(self.config_file),
                profile_name=self.current_profile
            )
            self.init_clients()
            console.print(f"\n✅ Conectado ao profile '{self.current_profile}'", style="green bold" if RICH_AVAILABLE else None)
            return True
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
            return False
    
    def init_clients(self):
        """Inicializa clientes OCI"""
        if not OCI_AVAILABLE:
            return
            
        try:
            self.clients = {
                'identity': oci.identity.IdentityClient(self.config),
                'compute': oci.core.ComputeClient(self.config),
                'network': oci.core.VirtualNetworkClient(self.config),
                'storage': oci.core.BlockstorageClient(self.config)
            }
        except Exception as e:
            console.print(f"⚠️  Alguns clientes não puderam ser inicializados: {e}", style="yellow" if RICH_AVAILABLE else None)
    
    def main_menu(self):
        """Menu principal"""
        while True:
            self.show_banner()
            
            menu_text = """
═══════════════════════════════════════════════════════════

[1] 🔍 Discovery Rápido
[2] 📊 Dashboard
[3] 🖥️  Gerenciar Instâncias
[4] 🌐 Gerenciar Rede Avançado
[5] 🔒 Security Lists Manager
[6] 🔐 IPSec VPN
[7] 🗑️  Deletar VCN (com dependências)
[8] 💰 Análise de Custos
[9] 📝 Relatórios
[10] 🔄 Trocar Profile
[0] Sair

═══════════════════════════════════════════════════════════
            """
            
            if RICH_AVAILABLE:
                menu = Panel(menu_text, title=f"Menu Principal - {self.current_profile}", expand=False, style="cyan")
                console.print(menu)
                choice = Prompt.ask("Escolha uma opção")
            else:
                print(menu_text)
                print(f"Profile Atual: {self.current_profile}")
                choice = input("Escolha uma opção: ")
            
            if choice == "0":
                if RICH_AVAILABLE:
                    if Confirm.ask("Deseja sair?"):
                        console.print("👋 Até logo!", style="cyan")
                        break
                else:
                    confirm = input("Deseja sair? (s/n): ")
                    if confirm.lower() == 's':
                        print("👋 Até logo!")
                        break
            elif choice == "1":
                self.discovery()
            elif choice == "2":
                self.dashboard()
            elif choice == "3":
                self.manage_instances()
            elif choice == "4":
                self.advanced_network_menu()
            elif choice == "5":
                self.manage_security_lists()
            elif choice == "6":
                self.manage_ipsec()
            elif choice == "7":
                self.delete_vcn_wizard()
            elif choice == "8":
                self.cost_analysis()
            elif choice == "9":
                self.generate_report()
            elif choice == "10":
                self.select_profile()
    
    def discovery(self):
        """Discovery de recursos"""
        console.print("\n🔍 DISCOVERY RÁPIDO", style="bold cyan" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            # Listar compartimentos
            console.print("\n📦 Descobrindo recursos...", style="cyan" if RICH_AVAILABLE else None)
            
            compartments = self.clients['identity'].list_compartments(
                self.config['tenancy'],
                compartment_id_in_subtree=True
            ).data
            
            console.print(f"✓ Compartimentos: {len(compartments) + 1}")  # +1 for root
            
            # Listar instâncias
            instances = self.clients['compute'].list_instances(
                compartment_id=self.config['tenancy']
            ).data
            
            console.print(f"✓ Instâncias: {len(instances)}")
            
            # Listar VCNs
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            console.print(f"✓ VCNs: {len(vcns)}")
            
            # Security Lists
            sls = self.clients['network'].list_security_lists(
                compartment_id=self.config['tenancy']
            ).data
            
            console.print(f"✓ Security Lists: {len(sls)}")
            
            # Mostrar instâncias
            if instances:
                console.print("\n📦 Instâncias encontradas:", style="yellow" if RICH_AVAILABLE else None)
                for inst in instances:
                    status = "🟢" if inst.lifecycle_state == "RUNNING" else "🔴"
                    console.print(f"  {status} {inst.display_name} - {inst.shape}")
            
            # Mostrar VCNs
            if vcns:
                console.print("\n🌐 VCNs encontradas:", style="yellow" if RICH_AVAILABLE else None)
                for vcn in vcns:
                    console.print(f"  • {vcn.display_name} ({vcn.cidr_block})")
            
            # Alertas de segurança
            open_ports_count = 0
            for sl in sls:
                for rule in sl.ingress_security_rules:
                    if rule.source == "0.0.0.0/0":
                        open_ports_count += 1
            
            if open_ports_count > 0:
                console.print(f"\n⚠️  {open_ports_count} regras com portas abertas para internet (0.0.0.0/0)", 
                            style="yellow bold" if RICH_AVAILABLE else None)
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER para continuar...")
    
    def dashboard(self):
        """Dashboard de recursos"""
        console.print("\n📊 DASHBOARD", style="bold cyan" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            # Estatísticas
            instances = self.clients['compute'].list_instances(
                compartment_id=self.config['tenancy']
            ).data
            
            running = len([i for i in instances if i.lifecycle_state == "RUNNING"])
            stopped = len([i for i in instances if i.lifecycle_state == "STOPPED"])
            
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            sls = self.clients['network'].list_security_lists(
                compartment_id=self.config['tenancy']
            ).data
            
            if RICH_AVAILABLE:
                # Cards com Rich
                cards = []
                
                compute_card = Panel(
                    f"[bold green]Running: {running}[/bold green]\n"
                    f"[bold red]Stopped: {stopped}[/bold red]\n"
                    f"[bold]Total: {len(instances)}[/bold]",
                    title="🖥️ Compute",
                    border_style="green"
                )
                cards.append(compute_card)
                
                network_card = Panel(
                    f"[bold]VCNs: {len(vcns)}[/bold]\n"
                    f"[bold]Security Lists: {len(sls)}[/bold]",
                    title="🌐 Network",
                    border_style="blue"
                )
                cards.append(network_card)
                
                console.print(Columns(cards))
            else:
                # Versão simples sem Rich
                print("\n╔══════════════════════════════╗")
                print("║         🖥️ COMPUTE           ║")
                print("╠══════════════════════════════╣")
                print(f"║ Running:  {running:19}║")
                print(f"║ Stopped:  {stopped:19}║")
                print(f"║ Total:    {len(instances):19}║")
                print("╚══════════════════════════════╝")
                
                print("\n╔══════════════════════════════╗")
                print("║         🌐 NETWORK           ║")
                print("╠══════════════════════════════╣")
                print(f"║ VCNs:           {len(vcns):13}║")
                print(f"║ Security Lists: {len(sls):13}║")
                print("╚══════════════════════════════╝")
            
            # Lista de instâncias
            if instances:
                console.print("\n🖥️ INSTÂNCIAS:", style="bold yellow" if RICH_AVAILABLE else None)
                
                for inst in instances[:5]:  # Top 5
                    status = "🟢" if inst.lifecycle_state == "RUNNING" else "🔴"
                    console.print(f"{status} {inst.display_name} - {inst.shape} - {inst.lifecycle_state}")
                
                if len(instances) > 5:
                    console.print(f"... e mais {len(instances) - 5} instância(s)")
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER para continuar...")
    
    def manage_instances(self):
        """Gerenciar instâncias"""
        console.print("\n🖥️ GERENCIAR INSTÂNCIAS", style="bold cyan" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            instances = self.clients['compute'].list_instances(
                compartment_id=self.config['tenancy']
            ).data
            
            if not instances:
                console.print("Nenhuma instância encontrada", style="yellow" if RICH_AVAILABLE else None)
                input("\nPressione ENTER...")
                return
            
            # Listar instâncias
            console.print("\nInstâncias disponíveis:", style="yellow" if RICH_AVAILABLE else None)
            for i, inst in enumerate(instances, 1):
                status = "🟢" if inst.lifecycle_state == "RUNNING" else "🔴"
                console.print(f"{i}. {status} {inst.display_name} - {inst.lifecycle_state}")
            
            console.print("\n📋 Ações:")
            console.print("1. Iniciar instância")
            console.print("2. Parar instância")
            console.print("3. Reiniciar instância")
            console.print("0. Voltar")
            
            action = input("\nEscolha a ação: ")
            
            if action in ["1", "2", "3"]:
                inst_num = int(input("Número da instância: ")) - 1
                
                if 0 <= inst_num < len(instances):
                    instance = instances[inst_num]
                    
                    if action == "1" and instance.lifecycle_state == "STOPPED":
                        console.print(f"Iniciando {instance.display_name}...")
                        self.clients['compute'].instance_action(instance.id, "START")
                        console.print("✅ Comando enviado", style="green" if RICH_AVAILABLE else None)
                        
                    elif action == "2" and instance.lifecycle_state == "RUNNING":
                        confirm = input(f"⚠️  Parar {instance.display_name}? (s/n): ")
                        if confirm.lower() == 's':
                            self.clients['compute'].instance_action(instance.id, "STOP")
                            console.print("✅ Comando enviado", style="green" if RICH_AVAILABLE else None)
                            
                    elif action == "3" and instance.lifecycle_state == "RUNNING":
                        self.clients['compute'].instance_action(instance.id, "SOFTRESET")
                        console.print("✅ Comando enviado", style="green" if RICH_AVAILABLE else None)
                    else:
                        console.print("⚠️  Ação não aplicável ao estado atual da instância", 
                                    style="yellow" if RICH_AVAILABLE else None)
            
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER para continuar...")
    
    def advanced_network_menu(self):
        """Menu avançado de rede"""
        while True:
            if RICH_AVAILABLE:
                console.clear()
            else:
                os.system('clear')
                
            console.print("\n🌐 GERENCIAMENTO AVANÇADO DE REDE", style="bold cyan" if RICH_AVAILABLE else None)
            
            print("""
1. Listar VCNs
2. Listar Subnets
3. Internet Gateways
4. NAT Gateways
5. Route Tables
6. DRG Management
7. 🗑️  Deletar VCN (com todas as dependências)
0. Voltar
            """)
            
            choice = input("Escolha uma opção: ")
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_vcns()
            elif choice == "2":
                self.list_subnets()
            elif choice == "3":
                self.list_internet_gateways()
            elif choice == "4":
                self.list_nat_gateways()
            elif choice == "5":
                self.list_route_tables()
            elif choice == "6":
                self.manage_drg()
            elif choice == "7":
                self.delete_vcn_wizard()
            else:
                console.print("⚠️  Opção inválida", style="yellow" if RICH_AVAILABLE else None)
                input("\nPressione ENTER...")
    
    def list_vcns(self):
        """Lista VCNs"""
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
            
        try:
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            if vcns:
                console.print("\n🌐 VCNs encontradas:", style="bold cyan" if RICH_AVAILABLE else None)
                for i, vcn in enumerate(vcns, 1):
                    console.print(f"{i}. {vcn.display_name}")
                    console.print(f"   CIDR: {vcn.cidr_block}")
                    console.print(f"   Estado: {vcn.lifecycle_state}")
                    
                    # Contar subnets
                    subnets = self.clients['network'].list_subnets(
                        compartment_id=self.config['tenancy'],
                        vcn_id=vcn.id
                    ).data
                    console.print(f"   Subnets: {len(subnets)}")
                    print()
            else:
                console.print("Nenhuma VCN encontrada", style="yellow" if RICH_AVAILABLE else None)
                
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def list_subnets(self):
        """Lista todas as subnets de todas as VCNs"""
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
            
        try:
            # Primeiro, listar todas as VCNs
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            if not vcns:
                console.print("Nenhuma VCN encontrada", style="yellow" if RICH_AVAILABLE else None)
                input("\nPressione ENTER...")
                return
                
            console.print("\n🌐 SUBNETS POR VCN:", style="bold cyan" if RICH_AVAILABLE else None)
            
            total_subnets = 0
            for vcn in vcns:
                subnets = self.clients['network'].list_subnets(
                    compartment_id=self.config['tenancy'],
                    vcn_id=vcn.id
                ).data
                
                if subnets:
                    console.print(f"\n📍 VCN: {vcn.display_name} ({vcn.cidr_block})")
                    for i, subnet in enumerate(subnets, 1):
                        # Tipo de subnet
                        subnet_type = "🌍 Pública" if not subnet.prohibit_internet_ingress else "🔒 Privada"
                        
                        console.print(f"  {i}. {subnet.display_name}")
                        console.print(f"     CIDR: {subnet.cidr_block}")
                        console.print(f"     Tipo: {subnet_type}")
                        console.print(f"     AD: {subnet.availability_domain or 'Regional'}")
                        console.print(f"     Estado: {subnet.lifecycle_state}")
                        
                        # Contar IPs usados
                        if hasattr(subnet, 'available_ip_address_count'):
                            total_ips = sum(1 for _ in ipaddress.ip_network(subnet.cidr_block).hosts())
                            used_ips = total_ips - subnet.available_ip_address_count
                            console.print(f"     IPs: {used_ips}/{total_ips} utilizados")
                        
                        print()
                    total_subnets += len(subnets)
            
            console.print(f"\n📊 Total: {total_subnets} subnet(s) encontrada(s)", 
                         style="green" if RICH_AVAILABLE else None)
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")

    def list_internet_gateways(self):
        """Lista Internet Gateways"""
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
            
        try:
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            console.print("\n🌍 INTERNET GATEWAYS:", style="bold cyan" if RICH_AVAILABLE else None)
            
            total_igs = 0
            for vcn in vcns:
                igs = self.clients['network'].list_internet_gateways(
                    compartment_id=self.config['tenancy'],
                    vcn_id=vcn.id
                ).data
                
                if igs:
                    console.print(f"\n📍 VCN: {vcn.display_name}")
                    for i, ig in enumerate(igs, 1):
                        status = "🟢 Habilitado" if ig.is_enabled else "🔴 Desabilitado"
                        console.print(f"  {i}. {ig.display_name}")
                        console.print(f"     Status: {status}")
                        console.print(f"     Estado: {ig.lifecycle_state}")
                        if hasattr(ig, 'route_table_id') and ig.route_table_id:
                            rt = self.clients['network'].get_route_table(ig.route_table_id).data
                            console.print(f"     Route Table: {rt.display_name}")
                        print()
                    total_igs += len(igs)
            
            if total_igs == 0:
                console.print("Nenhum Internet Gateway encontrado", style="yellow" if RICH_AVAILABLE else None)
            else:
                console.print(f"\n📊 Total: {total_igs} Internet Gateway(s)", 
                             style="green" if RICH_AVAILABLE else None)
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")

    def list_nat_gateways(self):
        """Lista NAT Gateways"""
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
            
        try:
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            console.print("\n🔀 NAT GATEWAYS:", style="bold cyan" if RICH_AVAILABLE else None)
            
            total_nats = 0
            for vcn in vcns:
                nats = self.clients['network'].list_nat_gateways(
                    compartment_id=self.config['tenancy'],
                    vcn_id=vcn.id
                ).data
                
                if nats:
                    console.print(f"\n📍 VCN: {vcn.display_name}")
                    for i, nat in enumerate(nats, 1):
                        block_traffic = "🚫 Bloqueado" if nat.block_traffic else "✅ Permitido"
                        console.print(f"  {i}. {nat.display_name}")
                        console.print(f"     IP Público: {nat.nat_ip}")
                        console.print(f"     Tráfego: {block_traffic}")
                        console.print(f"     Estado: {nat.lifecycle_state}")
                        print()
                    total_nats += len(nats)
            
            if total_nats == 0:
                console.print("Nenhum NAT Gateway encontrado", style="yellow" if RICH_AVAILABLE else None)
            else:
                console.print(f"\n📊 Total: {total_nats} NAT Gateway(s)", 
                             style="green" if RICH_AVAILABLE else None)
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")

    def list_route_tables(self):
        """Lista Route Tables"""
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
            
        try:
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            console.print("\n🗺️  ROUTE TABLES:", style="bold cyan" if RICH_AVAILABLE else None)
            
            total_rts = 0
            for vcn in vcns:
                rts = self.clients['network'].list_route_tables(
                    compartment_id=self.config['tenancy'],
                    vcn_id=vcn.id
                ).data
                
                if rts:
                    console.print(f"\n📍 VCN: {vcn.display_name}")
                    for i, rt in enumerate(rts, 1):
                        rt_type = "🔧 Default" if rt.display_name.startswith("Default") else "👤 Custom"
                        console.print(f"  {i}. {rt.display_name}")
                        console.print(f"     Tipo: {rt_type}")
                        console.print(f"     Regras: {len(rt.route_rules)}")
                        console.print(f"     Estado: {rt.lifecycle_state}")
                        
                        # Mostrar algumas regras principais
                        if rt.route_rules:
                            console.print("     📋 Regras principais:")
                            for j, rule in enumerate(rt.route_rules[:3], 1):  # Primeiras 3 regras
                                destination = rule.destination
                                target_type = "Internet Gateway" if rule.network_entity_id and "internetgateway" in rule.network_entity_id else "Outros"
                                console.print(f"        {j}. {destination} → {target_type}")
                            
                            if len(rt.route_rules) > 3:
                                console.print(f"        ... e mais {len(rt.route_rules) - 3} regra(s)")
                        print()
                    total_rts += len(rts)
            
            if total_rts == 0:
                console.print("Nenhuma Route Table encontrada", style="yellow" if RICH_AVAILABLE else None)
            else:
                console.print(f"\n📊 Total: {total_rts} Route Table(s)", 
                             style="green" if RICH_AVAILABLE else None)
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")

    def manage_drg(self):
        """Gerenciar Dynamic Routing Gateways (DRG)"""
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
            
        try:
            console.print("\n🔀 DYNAMIC ROUTING GATEWAYS (DRG):", style="bold cyan" if RICH_AVAILABLE else None)
            
            drgs = self.clients['network'].list_drgs(
                compartment_id=self.config['tenancy']
            ).data
            
            if drgs:
                console.print(f"\n📡 {len(drgs)} DRG(s) encontrado(s):")
                
                for i, drg in enumerate(drgs, 1):
                    console.print(f"\n{i}. {drg.display_name}")
                    console.print(f"   Estado: {drg.lifecycle_state}")
                    
                    # Listar attachments da DRG
                    try:
                        attachments = self.clients['network'].list_drg_attachments(
                            compartment_id=self.config['tenancy'],
                            drg_id=drg.id
                        ).data
                        
                        console.print(f"   Attachments: {len(attachments)}")
                        
                        for att in attachments:
                            att_type = "VCN" if att.vcn_id else "Virtual Circuit" if hasattr(att, 'virtual_circuit_id') else "Outros"
                            console.print(f"     • {att.display_name} ({att_type}) - {att.lifecycle_state}")
                            
                    except Exception as e:
                        console.print(f"     ⚠️  Erro ao listar attachments: {e}", style="yellow" if RICH_AVAILABLE else None)
                    
                    # Verificar route tables da DRG
                    try:
                        drg_route_tables = self.clients['network'].list_drg_route_tables(
                            drg_id=drg.id
                        ).data
                        
                        console.print(f"   Route Tables: {len(drg_route_tables)}")
                        
                    except Exception as e:
                        console.print(f"     ⚠️  Erro ao listar route tables: {e}", style="yellow" if RICH_AVAILABLE else None)
            else:
                console.print("Nenhum DRG encontrado", style="yellow" if RICH_AVAILABLE else None)
                console.print("\n💡 DRGs são usados para conectar VCNs entre si ou com redes on-premises")
                console.print("   através de FastConnect ou VPN.")
                    
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def delete_vcn_wizard(self):
        """Wizard para deletar VCN com dependências - VERSÃO CORRIGIDA"""
        console.print("\n🗑️ DELETAR VCN COM DEPENDÊNCIAS", style="bold red" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            if not vcns:
                console.print("Nenhuma VCN encontrada", style="yellow" if RICH_AVAILABLE else None)
                input("\nPressione ENTER...")
                return
            
            # Listar VCNs
            console.print("\n📋 VCNs disponíveis:")
            for i, vcn in enumerate(vcns, 1):
                console.print(f"{i}. {vcn.display_name} ({vcn.cidr_block})")
            
            vcn_num = int(input("\nNúmero da VCN para deletar (0 para cancelar): ")) - 1
            
            if vcn_num < 0:
                return
                
            if 0 <= vcn_num < len(vcns):
                vcn = vcns[vcn_num]
                
                console.print(f"\n⚠️  ATENÇÃO: Isso irá deletar:", style="yellow bold" if RICH_AVAILABLE else None)
                console.print(f"• VCN: {vcn.display_name}")
                console.print("• Todas as Subnets")
                console.print("• Todos os Gateways (Internet, NAT, Service)")
                console.print("• Todos os Network Security Groups (NSGs)")
                console.print("• Todas as Route Tables customizadas")
                console.print("• Todas as Security Lists customizadas")
                console.print("• ⚠️  Instâncias usando esta VCN podem ficar inacessíveis!")
                
                confirm = input("\n⚠️  Tem certeza? Digite 'DELETAR' para confirmar: ")
                
                if confirm == "DELETAR":
                    console.print("\n🔄 Iniciando processo de deleção...", style="yellow" if RICH_AVAILABLE else None)
                    
                    try:
                        import time
                        
                        # 1. Verificar instâncias
                        console.print("• Verificando instâncias...")
                        instances = self.clients['compute'].list_instances(
                            compartment_id=self.config['tenancy']
                        ).data
                        
                        instances_in_vcn = []
                        for instance in instances:
                            try:
                                vnics = self.clients['compute'].list_vnic_attachments(
                                    compartment_id=self.config['tenancy'],
                                    instance_id=instance.id
                                ).data
                                
                                for vnic_att in vnics:
                                    if vnic_att.lifecycle_state in ['ATTACHED', 'ATTACHING']:
                                        vnic = self.clients['network'].get_vnic(vnic_att.vnic_id).data
                                        subnet = self.clients['network'].get_subnet(vnic.subnet_id).data
                                        if subnet.vcn_id == vcn.id:
                                            instances_in_vcn.append(instance)
                                            break
                            except Exception as e:
                                console.print(f"    ⚠️  Erro verificando instância {instance.display_name}: {e}")
                        
                        if instances_in_vcn:
                            console.print(f"  ⚠️  {len(instances_in_vcn)} instância(s) usando esta VCN!", 
                                        style="red bold" if RICH_AVAILABLE else None)
                            for inst in instances_in_vcn:
                                console.print(f"    - {inst.display_name}")
                            
                            proceed = input("\n  Continuar mesmo assim? (s/n): ")
                            if proceed.lower() != 's':
                                console.print("Operação cancelada", style="yellow" if RICH_AVAILABLE else None)
                                input("\nPressione ENTER...")
                                return
                        
                        # 2. PRIMEIRO: Limpar referências nas Route Tables
                        console.print("• Limpando referências em Route Tables...")
                        rts = self.clients['network'].list_route_tables(
                            compartment_id=self.config['tenancy'],
                            vcn_id=vcn.id
                        ).data
                        
                        for rt in rts:
                            if rt.route_rules:  # Se tem regras
                                console.print(f"  Limpando regras da Route Table {rt.display_name}...")
                                try:
                                    # Limpar todas as regras primeiro
                                    update_details = oci.core.models.UpdateRouteTableDetails(
                                        route_rules=[]  # Lista vazia remove todas as regras
                                    )
                                    self.clients['network'].update_route_table(rt.id, update_details)
                                    time.sleep(2)  # Aguardar propagação
                                    
                                except Exception as e:
                                    console.print(f"    ⚠️  Erro limpando Route Table {rt.display_name}: {e}")
                        
                        # 3. Deletar Subnets
                        console.print("• Deletando subnets...")
                        subnets = self.clients['network'].list_subnets(
                            compartment_id=self.config['tenancy'],
                            vcn_id=vcn.id
                        ).data
                        
                        for subnet in subnets:
                            console.print(f"  Deletando subnet {subnet.display_name}...")
                            try:
                                self.clients['network'].delete_subnet(subnet.id)
                                time.sleep(1)  # Aguardar
                            except Exception as e:
                                console.print(f"    ⚠️  Erro: {e}")
                        
                        # 4. Aguardar subnets serem deletadas
                        console.print("• Aguardando deleção das subnets...")
                        max_wait = 60  # 60 segundos máximo
                        wait_time = 0
                        
                        while wait_time < max_wait:
                            remaining_subnets = self.clients['network'].list_subnets(
                                compartment_id=self.config['tenancy'],
                                vcn_id=vcn.id
                            ).data
                            
                            if not remaining_subnets:
                                break
                                
                            time.sleep(2)
                            wait_time += 2
                            console.print(f"  Aguardando... ({len(remaining_subnets)} subnets restantes)")
                        
                        # 5. Deletar Internet Gateways
                        console.print("• Deletando Internet Gateways...")
                        igs = self.clients['network'].list_internet_gateways(
                            compartment_id=self.config['tenancy'],
                            vcn_id=vcn.id
                        ).data
                        
                        for ig in igs:
                            console.print(f"  Deletando {ig.display_name}...")
                            try:
                                self.clients['network'].delete_internet_gateway(ig.id)
                                time.sleep(1)
                            except Exception as e:
                                console.print(f"    ⚠️  Erro: {e}")
                        
                        # 6. Deletar NAT Gateways
                        console.print("• Deletando NAT Gateways...")
                        nats = self.clients['network'].list_nat_gateways(
                            compartment_id=self.config['tenancy'],
                            vcn_id=vcn.id
                        ).data
                        
                        for nat in nats:
                            console.print(f"  Deletando {nat.display_name}...")
                            try:
                                self.clients['network'].delete_nat_gateway(nat.id)
                                time.sleep(1)
                            except Exception as e:
                                console.print(f"    ⚠️  Erro: {e}")
                        
                        # 7. Deletar Service Gateways
                        console.print("• Deletando Service Gateways...")
                        try:
                            sgs = self.clients['network'].list_service_gateways(
                                compartment_id=self.config['tenancy'],
                                vcn_id=vcn.id
                            ).data
                            
                            for sg in sgs:
                                console.print(f"  Deletando {sg.display_name}...")
                                try:
                                    self.clients['network'].delete_service_gateway(sg.id)
                                    time.sleep(1)
                                except Exception as e:
                                    console.print(f"    ⚠️  Erro: {e}")
                        except Exception as e:
                            console.print(f"    ⚠️  Erro listando Service Gateways: {e}")
                        
                        # 8. Deletar Network Security Groups (NSGs)
                        console.print("• Deletando Network Security Groups...")
                        try:
                            nsgs = self.clients['network'].list_network_security_groups(
                                compartment_id=self.config['tenancy'],
                                vcn_id=vcn.id
                            ).data
                            
                            for nsg in nsgs:
                                console.print(f"  Deletando NSG {nsg.display_name}...")
                                try:
                                    self.clients['network'].delete_network_security_group(nsg.id)
                                    time.sleep(1)
                                except Exception as e:
                                    console.print(f"    ⚠️  Erro: {e}")
                        except Exception as e:
                            console.print(f"    ⚠️  Erro listando NSGs: {e}")
                        
                        # 9. Deletar Route Tables customizadas (agora sem regras)
                        console.print("• Deletando Route Tables...")
                        rts = self.clients['network'].list_route_tables(
                            compartment_id=self.config['tenancy'],
                            vcn_id=vcn.id
                        ).data
                        
                        for rt in rts:
                            if not rt.display_name.startswith("Default"):
                                console.print(f"  Deletando {rt.display_name}...")
                                try:
                                    self.clients['network'].delete_route_table(rt.id)
                                    time.sleep(1)
                                except Exception as e:
                                    console.print(f"    ⚠️  Erro: {e}")
                        
                        # 10. Deletar Security Lists customizadas
                        console.print("• Deletando Security Lists...")
                        sls = self.clients['network'].list_security_lists(
                            compartment_id=self.config['tenancy'],
                            vcn_id=vcn.id
                        ).data
                        
                        for sl in sls:
                            if not sl.display_name.startswith("Default"):
                                console.print(f"  Deletando {sl.display_name}...")
                                try:
                                    self.clients['network'].delete_security_list(sl.id)
                                    time.sleep(1)
                                except Exception as e:
                                    console.print(f"    ⚠️  Erro: {e}")
                        
                        # 11. Aguardar todos os recursos serem deletados
                        console.print("• Aguardando finalização das deleções...")
                        time.sleep(10)
                        
                        # 12. Finalmente deletar a VCN
                        console.print(f"• Deletando VCN {vcn.display_name}...")
                        self.clients['network'].delete_vcn(vcn.id)
                        
                        console.print(f"\n✅ VCN '{vcn.display_name}' deletada com sucesso!", 
                                    style="green bold" if RICH_AVAILABLE else None)
                        
                    except Exception as e:
                        console.print(f"\n❌ Erro durante deleção: {e}", style="red" if RICH_AVAILABLE else None)
                        console.print("\n💡 Dica: Alguns recursos podem ter dependências. Tente novamente ou delete manualmente via console OCI.")
                else:
                    console.print("Operação cancelada", style="yellow" if RICH_AVAILABLE else None)
            
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def manage_security_lists(self):
        """Gerenciar Security Lists"""
        console.print("\n🔒 SECURITY LISTS MANAGER", style="bold cyan" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            sls = self.clients['network'].list_security_lists(
                compartment_id=self.config['tenancy']
            ).data
            
            if not sls:
                console.print("Nenhuma Security List encontrada", style="yellow" if RICH_AVAILABLE else None)
                input("\nPressione ENTER...")
                return
            
            # Listar security lists
            console.print("\n📋 Security Lists disponíveis:")
            for i, sl in enumerate(sls, 1):
                vcn = self.clients['network'].get_vcn(sl.vcn_id).data
                console.print(f"\n{i}. {sl.display_name}")
                console.print(f"   VCN: {vcn.display_name}")
                console.print(f"   Regras de Ingresso: {len(sl.ingress_security_rules)}")
                console.print(f"   Regras de Egresso: {len(sl.egress_security_rules)}")
                
                # Verificar portas abertas
                open_ports = []
                for rule in sl.ingress_security_rules:
                    if rule.source == "0.0.0.0/0":
                        if hasattr(rule, 'tcp_options') and rule.tcp_options:
                            if rule.tcp_options.destination_port_range:
                                port_range = rule.tcp_options.destination_port_range
                                open_ports.append(f"TCP:{port_range.min}-{port_range.max}")
                
                if open_ports:
                    console.print(f"   ⚠️  Portas abertas para internet: {', '.join(open_ports)}", 
                                style="yellow" if RICH_AVAILABLE else None)
            
            sl_num = input("\nNúmero da Security List para gerenciar (0 para voltar): ")
            
            if sl_num != "0":
                idx = int(sl_num) - 1
                if 0 <= idx < len(sls):
                    self.edit_security_list(sls[idx])
            
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def edit_security_list(self, sl):
        """Editar Security List"""
        console.print(f"\n📝 Editando: {sl.display_name}", style="cyan" if RICH_AVAILABLE else None)
        
        console.print("\n1. Adicionar regra comum (HTTP/HTTPS/SSH/etc)")
        console.print("2. Listar todas as regras")
        console.print("3. Remover regra")
        console.print("0. Voltar")
        
        choice = input("\nEscolha: ")
        
        if choice == "1":
            console.print("\n📋 Regras comuns:")
            console.print("1. HTTP (80)")
            console.print("2. HTTPS (443)")
            console.print("3. SSH (22)")
            console.print("4. RDP (3389)")
            console.print("5. MySQL (3306)")
            console.print("6. PostgreSQL (5432)")
            console.print("7. MongoDB (27017)")
            console.print("8. Redis (6379)")
            console.print("9. Custom")
            
            rule_choice = input("\nEscolha a regra: ")
            source = input("Source CIDR (default: 0.0.0.0/0): ") or "0.0.0.0/0"
            
            ports = {
                "1": (80, 80, "HTTP"),
                "2": (443, 443, "HTTPS"),
                "3": (22, 22, "SSH"),
                "4": (3389, 3389, "RDP"),
                "5": (3306, 3306, "MySQL"),
                "6": (5432, 5432, "PostgreSQL"),
                "7": (27017, 27017, "MongoDB"),
                "8": (6379, 6379, "Redis")
            }
            
            if rule_choice in ports:
                min_port, max_port, desc = ports[rule_choice]
            elif rule_choice == "9":
                min_port = int(input("Porta inicial: "))
                max_port = int(input("Porta final: "))
                desc = input("Descrição: ")
            else:
                console.print("Opção inválida", style="red" if RICH_AVAILABLE else None)
                return
            
            try:
                # Criar nova regra
                new_rule = oci.core.models.IngressSecurityRule(
                    protocol="6",  # TCP
                    source=source,
                    tcp_options=oci.core.models.TcpOptions(
                        destination_port_range=oci.core.models.PortRange(
                            min=min_port,
                            max=max_port
                        )
                    ),
                    description=f"{desc} access from {source}"
                )
                
                # Adicionar à lista
                sl.ingress_security_rules.append(new_rule)
                
                # Atualizar
                update_details = oci.core.models.UpdateSecurityListDetails(
                    ingress_security_rules=sl.ingress_security_rules,
                    egress_security_rules=sl.egress_security_rules
                )
                
                self.clients['network'].update_security_list(sl.id, update_details)
                console.print("✅ Regra adicionada com sucesso!", style="green" if RICH_AVAILABLE else None)
                
            except Exception as e:
                console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        elif choice == "2":
            # Listar regras
            console.print("\n📥 REGRAS DE INGRESSO:", style="bold yellow" if RICH_AVAILABLE else None)
            for i, rule in enumerate(sl.ingress_security_rules, 1):
                protocol = "TCP" if rule.protocol == "6" else ("UDP" if rule.protocol == "17" else rule.protocol)
                ports = "ALL"
                
                if hasattr(rule, 'tcp_options') and rule.tcp_options:
                    if rule.tcp_options.destination_port_range:
                        pr = rule.tcp_options.destination_port_range
                        ports = f"{pr.min}-{pr.max}" if pr.min != pr.max else str(pr.min)
                
                desc = rule.description or "Sem descrição"
                console.print(f"{i}. {rule.source} → {protocol}:{ports} - {desc}")
            
            console.print("\n📤 REGRAS DE EGRESSO:", style="bold yellow" if RICH_AVAILABLE else None)
            for i, rule in enumerate(sl.egress_security_rules, 1):
                protocol = "TCP" if rule.protocol == "6" else ("UDP" if rule.protocol == "17" else rule.protocol)
                console.print(f"{i}. {rule.destination} → {protocol}")
        
        elif choice == "3":
            console.print("\n⚠️  Funcionalidade de remoção em desenvolvimento", style="yellow" if RICH_AVAILABLE else None)
    
    def manage_ipsec(self):
        """Gerenciar IPSec VPN"""
        console.print("\n🔐 IPSEC VPN MANAGER", style="bold cyan" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            connections = self.clients['network'].list_ip_sec_connections(
                compartment_id=self.config['tenancy']
            ).data
            
            if connections:
                console.print(f"\n📡 {len(connections)} conexão(ões) IPSec encontrada(s):", 
                            style="green" if RICH_AVAILABLE else None)
                
                for conn in connections:
                    console.print(f"\n• {conn.display_name}")
                    console.print(f"  Estado: {conn.lifecycle_state}")
                    
                    # Verificar túneis
                    tunnels = self.clients['network'].list_ip_sec_connection_tunnels(conn.id).data
                    console.print(f"  Túneis: {len(tunnels)}")
                    
                    for i, tunnel in enumerate(tunnels, 1):
                        status = "🟢 UP" if tunnel.status == "UP" else "🔴 DOWN" if tunnel.status == "DOWN" else "🟡 " + tunnel.status
                        console.print(f"    Túnel {i}: {status}")
                        console.print(f"      VPN IP: {tunnel.vpn_ip}")
            else:
                console.print("Nenhuma conexão IPSec encontrada", style="yellow" if RICH_AVAILABLE else None)
                
        except Exception as e:
            console.print(f"⚠️  {e}", style="yellow" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def cost_analysis(self):
        """Análise de custos"""
        console.print("\n💰 ANÁLISE DE CUSTOS", style="bold cyan" if RICH_AVAILABLE else None)
        console.print("Nota: Requer permissões de billing", style="yellow" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        try:
            # Data range
            end_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = end_time - timedelta(days=30)
            
            # Tentar obter custos
            usage_client = oci.usage_api.UsageapiClient(self.config)
            
            request_details = oci.usage_api.models.RequestSummarizedUsagesDetails(
                tenant_id=self.config['tenancy'],
                time_usage_started=start_time,
                time_usage_ended=end_time,
                granularity="DAILY",
                query_type="COST"
            )
            
            response = usage_client.request_summarized_usages(request_details)
            
            if response.data.items:
                total = sum(float(item.computed_amount or 0) for item in response.data.items)
                console.print(f"\n💵 Custo total (30 dias): R$ {total:.2f}", 
                            style="green bold" if RICH_AVAILABLE else None)
                console.print(f"📊 Média diária: R$ {total/30:.2f}")
                console.print(f"📈 Projeção mensal: R$ {total:.2f}")
            else:
                console.print("Sem dados de custo disponíveis", style="yellow" if RICH_AVAILABLE else None)
                
        except Exception as e:
            console.print(f"⚠️  Sem acesso aos dados de custo: {str(e)[:50]}...", 
                        style="yellow" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def generate_report(self):
        """Gerar relatório"""
        console.print("\n📝 GERANDO RELATÓRIO", style="bold cyan" if RICH_AVAILABLE else None)
        
        if not OCI_AVAILABLE or not self.clients:
            console.print("⚠️  OCI SDK não disponível", style="yellow" if RICH_AVAILABLE else None)
            input("\nPressione ENTER...")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"report_{self.current_profile}_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "profile": self.current_profile,
            "resources": {}
        }
        
        try:
            console.print("Coletando dados...")
            
            # Instâncias
            instances = self.clients['compute'].list_instances(
                compartment_id=self.config['tenancy']
            ).data
            
            report['resources']['instances'] = [
                {
                    "name": i.display_name,
                    "state": i.lifecycle_state,
                    "shape": i.shape
                } for i in instances
            ]
            
            # VCNs
            vcns = self.clients['network'].list_vcns(
                compartment_id=self.config['tenancy']
            ).data
            
            report['resources']['vcns'] = [
                {
                    "name": v.display_name,
                    "cidr": v.cidr_block,
                    "state": v.lifecycle_state
                } for v in vcns
            ]
            
            # Security Lists
            sls = self.clients['network'].list_security_lists(
                compartment_id=self.config['tenancy']
            ).data
            
            report['resources']['security_lists'] = []
            for sl in sls:
                open_ports = []
                for rule in sl.ingress_security_rules:
                    if rule.source == "0.0.0.0/0":
                        if hasattr(rule, 'tcp_options') and rule.tcp_options:
                            if rule.tcp_options.destination_port_range:
                                pr = rule.tcp_options.destination_port_range
                                open_ports.append(f"TCP:{pr.min}-{pr.max}")
                
                report['resources']['security_lists'].append({
                    "name": sl.display_name,
                    "ingress_rules": len(sl.ingress_security_rules),
                    "egress_rules": len(sl.egress_security_rules),
                    "open_to_internet": open_ports
                })
            
            # Salvar
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            console.print(f"\n✅ Relatório salvo: {report_file}", style="green" if RICH_AVAILABLE else None)
            
            # Mostrar resumo
            console.print("\n📊 RESUMO:")
            console.print(f"• Instâncias: {len(instances)}")
            console.print(f"• VCNs: {len(vcns)}")
            console.print(f"• Security Lists: {len(sls)}")
            
            # Alertas
            open_count = sum(1 for sl in report['resources']['security_lists'] if sl['open_to_internet'])
            if open_count > 0:
                console.print(f"\n⚠️  {open_count} Security List(s) com portas abertas para internet", 
                            style="yellow bold" if RICH_AVAILABLE else None)
            
        except Exception as e:
            console.print(f"❌ Erro: {e}", style="red" if RICH_AVAILABLE else None)
        
        input("\nPressione ENTER...")
    
    def run(self):
        """Executa o manager"""
        self.show_banner()
        
        if self.select_profile():
            self.main_menu()

if __name__ == "__main__":
    try:
        manager = OCIManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido. Até logo!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)