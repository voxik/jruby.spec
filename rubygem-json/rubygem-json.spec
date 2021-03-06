%global	gem_name	json
%global	rubyabi	1.9.1
%global	with_jruby_ext 1

Name:           rubygem-%{gem_name}
Version:        1.6.5
Release:        5%{?dist}

Summary:        A JSON implementation in Ruby

Group:          Development/Languages

License:        Ruby or GPLv2
URL:            http://json.rubyforge.org
Source0:        http://gems.rubyforge.org/gems/%{gem_name}-%{version}.gem
%if 0%{?with_jruby_ext}
Source1:        http://gems.rubyforge.org/gems/%{gem_name}-%{version}-java.gem
Patch0:         json-add-classpath-to-jar-build.patch

BuildRequires:  java-devel
BuildRequires:  jpackage-utils
BuildRequires:  jruby
# when doing gem-jruby install, rdoc needs json_pure, because it can't load MRI
# json's ext - worse dep loop than in MRI :(
BuildRequires:  rubygem-json_pure
%endif
BuildRequires:	ruby(abi) = %{rubyabi}
BuildRequires:	ruby-devel
BuildRequires:  rubygems-devel
BuildRequires:  rubygem(rake)
BuildRequires:	rubygem(minitest)
BuildRequires:	rubygem(bigdecimal)
Requires:       ruby
Requires:       ruby(abi) = %{rubyabi}
Requires:       rubygems
Provides:       rubygem(json) = %{version}

Obsoletes:	rubygem-%{gem_name}-gui < %{version}
Obsoletes:	ruby-%{gem_name}-gui < %{version}
Obsoletes:	ruby-%{gem_name} < %{version}

%description
This is a implementation of the JSON specification according
to RFC 4627 in Ruby.
You can think of it as a low fat alternative to XML,
if you want to store data to disk or transmit it over
a network rather than use a verbose markup language.

%package	doc
Summary:	Documentation for %{name}
Group:		Documentation

Requires:	%{name} = %{version}-%{release}

%description	doc
This package contains documentation for %{name}.

%if 0%{?with_jruby_ext}
%package	jruby
Summary:	JRuby extension for %{name}
Group:		Development/Languages

Requires:	%{name} = %{version}-%{release}
Requires:       jruby

%description	jruby
This package contains JRuby extension for %{name}.
%endif

%prep
%setup -q -c -T
mkdir -p ./%{gem_dir}
export CONFIGURE_ARGS="--with-cflags='%{optflags}'"
gem install --local --install-dir .%{gem_dir} -V --force %{SOURCE0}

%if 0%{with_jruby_ext}
gem-jruby install --local --install-dir .%{gem_dir} -V --force %{SOURCE1}
pushd .%{gem_instdir}
%patch0
popd
%endif

%build

find . -name \*gem -exec chmod 0644 {} \;

# change cflags to honor Fedora compiler flags correctly
find . -name extconf.rb | xargs sed -i -e 's|-O3|-O2|'
find . -name Makefile | xargs sed -i -e 's|-O3|-O2|'
# compile again
find . -name extconf.rb | while read f
do
	make -C $(dirname $f) clean all install
done

# remove pure
rm -fr .%{gem_instdir}/lib/json/pure*

%if 0%{?with_jruby_ext}

pushd .%{gem_instdir}
CLASSPATH=$(build-classpath bytelist jnr-constants jcodings)
sed -i "s|CLASSPATH|$CLASSPATH|" Rakefile
JAVA_HOME=%{java_home} jruby -S rake create_jar
popd
%endif

%install
mkdir -p $RPM_BUILD_ROOT%{gem_dir}
mkdir -p $RPM_BUILD_ROOT%{gem_extdir}/ext/%{gem_name}/ext
 
cp -a .%{gem_dir}/* %{buildroot}/%{gem_dir}

%if 0%{?with_jruby_ext}
# the noarch part is common, so just link to it
rm -fr %{buildroot}%{gem_instdir_jruby}
ln -s %{gem_instdir} %{buildroot}%{gem_instdir_jruby}
# create java extdir and make the gemspec aware of extensions, so that they get loaded
mkdir -p $RPM_BUILD_ROOT%{gem_extdir_jruby}/ext/%{gem_name}/ext/%{gem_name}/ext
cp -a .%{gem_instdir}/lib/json/ext/*.jar $RPM_BUILD_ROOT%{gem_extdir_jruby}/ext/%{gem_name}/ext/%{gem_name}/ext
sed -i 's|"lib"]|"ext/json/ext", "ext", "lib"]\ns.extensions = ["doesnt_matter_whats_here"]|' %{buildroot}%{gem_spec_jruby}
%endif

# Let's move arch dependent files to arch specific directory
cp -a ./%{gem_instdir}/ext/json/ext/json \
	$RPM_BUILD_ROOT%{gem_extdir}/ext/%{gem_name}/ext

chmod 0644 $RPM_BUILD_ROOT%{gem_instdir}/install.rb
chmod 0644 $RPM_BUILD_ROOT%{gem_instdir}/tests/*.rb
chmod 0644 $RPM_BUILD_ROOT%{gem_instdir}/tools/server.rb
chmod 0644 $RPM_BUILD_ROOT%{gem_instdir}/tools/fuzz.rb
chmod 0644 $RPM_BUILD_ROOT%{gem_instdir}/benchmarks/*.rb

# We don't need those files anymore.
rm -rf $RPM_BUILD_ROOT%{gem_instdir}/ext
rm -rf $RPM_BUILD_ROOT%{gem_instdir}/install.rb
rm -rf $RPM_BUILD_ROOT%{gem_instdir}/{.require_paths,.gitignore,.travis.yml}
rm -rf $RPM_BUILD_ROOT%{gem_instdir}/lib/json/ext/
rm -rf $RPM_BUILD_ROOT%{gem_instdir}/diagrams
rm -rf $RPM_BUILD_ROOT%{gem_docdir}/rdoc/classes/.src
rm -rf $RPM_BUILD_ROOT%{gem_docdir}/rdoc/classes/.html

rm -rf $RPM_BUILD_ROOT%{gem_instdir}/java/

%check
pushd .%{gem_instdir}
ruby -S testrb -Ilib:ext/%{gem_name}/ext $(ls -1 tests/test_*.rb | sort)
popd


%files
%defattr(-,root,root,-)
%doc %{gem_instdir}/[A-Z]*
%exclude	%{gem_instdir}/Rakefile
%dir %{gem_instdir}
%dir %{gem_instdir}/lib
%dir %{gem_instdir}/lib/%{gem_name}
%{gem_instdir}/tools/
%{gem_instdir}/lib/%{gem_name}.rb
%{gem_instdir}/lib/%{gem_name}/add
%{gem_instdir}/lib/%{gem_name}/common.rb
%{gem_instdir}/lib/%{gem_name}/ext.rb
%{gem_instdir}/lib/%{gem_name}/version.rb
%{gem_extdir}/
%{gem_cache}
%{gem_spec}

%files      doc
%defattr(-,root,root,-)
%{gem_instdir}/Rakefile
%{gem_instdir}/data
%{gem_instdir}/tests
%{gem_instdir}/benchmarks
%{gem_instdir}/*gemspec
#%{gem_instdir}/doc-main.txt
%{gem_docdir}/

%if 0%{?with_jruby_ext}
%files      jruby
%defattr(-,root,root,-)
%exclude %{gem_cache_jruby}
%{gem_instdir_jruby}
%{gem_spec_jruby}
%{gem_extdir_jruby}
%endif

%changelog
* Tue Dec 04 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.6.5-5
- Utilize even newer JRuby macros :)

* Fri Nov 02 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.6.5-4
- Use the -java gem to get separate gemspec for JRuby ext.
- Utilize new RubyGems JRuby macros.

* Mon Oct 08 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.6.5-3
- Provide Java extension for use with JRuby.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jan 21 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.6.5-1
- 1.6.5

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 jkeating - 1.4.6-2
- Rebuilt for gcc bug 634757

* Sat Sep 18 2010 Xavier Lamien <laxathom@fedoraproject.org> - 1.4.6-1
- Update release.
- Enabled test stage.

* Fri Jun 11 2010 Xavier Lamien <laxathom@fedoraproject.org> - 1.4.3-3
- Move ruby's site_lib editor to ruby-json-gui.

* Mon May 10 2010 Xavier Lamien <laxathom@fedoraproject.org> - 1.4.3-2
- Move editor out of ruby-json sub-package.

* Sun May 09 2010 Xavier Lamien <laxathom@fedoraproject.org> - 1.4.3-1
- Update release.
- Split-out json editor.

* Thu Oct 29 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.9-1
- Update release.

* Wed Aug 12 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.7-3
- Fix gem scripts and install_dir.
- Enable %%check stage.

* Wed Aug 05 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.7-2
- Rebuild in correct buildir process.
- Add sub packages.

* Mon Aug 03 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.7-1
- Update release.

* Sat Jun 06 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.6-1
- Update release.

* Tue May 12 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.5-1
- Update release.

* Thu Apr 02 2009 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.4-1
- Update release.

* Sat Jul 12 2008 Xavier Lamien <laxathom@fedoraproject.org> - 1.1.3-1
- Initial RPM release.
