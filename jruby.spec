%global jruby_vendordir %{_datadir}/%{name}/lib
%global jruby_sitedir %{_prefix}/local/share/%{name}/lib
%global rubygems_dir %{_datadir}/rubygems

%global git_hash 4a6bb0a

%global yecht_commitversion 6009fd7
%global yecht_dlversion 0.0.2-0-g%{yecht_commitversion}
%global yecht_cluster olabini

#%%global preminorver RC2
%global release 1
%global enable_check 1

Name:           jruby
Version:        1.7.0
Release:        %{?preminorver:0.}%{release}%{?preminorver:.%{preminorver}}%{?dist}
Summary:        Pure Java implementation of the Ruby interpreter
Group:          Development/Languages
License:        (CPL or GPLv2+ or LGPLv2+) and ASL 1.1 and MIT and Ruby
URL:            http://jruby.org/
BuildArch:      noarch
Source0:        http://jruby.org.s3.amazonaws.com/downloads/1.7.0/jruby-src-1.7.0.tar.gz
Source1:        http://github.com/%{yecht_cluster}/yecht/tarball/0.0.2/%{yecht_cluster}-yecht-%{yecht_dlversion}.tar.gz
Patch0:         jruby-executable-add-fedora-java-opts-stub.patch
Patch1:         jruby-add-classpath-to-start-script.patch
Patch2:         jruby-dont-include-jar-dependencies-in-build-xml.patch
Patch3:         jruby-no-jar-bundling.patch
# UDP multicast test hangs
# http://jira.codehaus.org/browse/JRUBY-6758
Patch4:         jruby-comment-out-hanging-socket-test.patch

# this patch contains the following upstream change
# https://github.com/jruby/jruby/commit/6c1d41aedfde705c969abf10cf5384e2be69f10a
# -- not any more, it changes the change to be ok downstream :)
Patch6:         jruby-remove-builtin-yecht-jar.patch

Patch7:         jruby-yecht-only-build-bindings.patch

Patch9:         jruby-remove-rubygems-dirs-definition.patch

BuildRequires:  ant >= 1.6
BuildRequires:  ant-junit
BuildRequires:  java-devel >= 1.6
BuildRequires:  jpackage-utils >= 1.5

BuildRequires:  bouncycastle
BuildRequires:  bouncycastle-mail
BuildRequires:  bsf
BuildRequires:  bytelist >= 1.0.8
BuildRequires:  coro-mock
BuildRequires:  felix-osgi-core >= 1.4.0
BuildRequires:  invokebinder
BuildRequires:  jansi
BuildRequires:  jarjar
BuildRequires:  jline2 >= 2.7
BuildRequires:  jffi >= 1.0.10
BuildRequires:  jna
BuildRequires:  jnr-constants
BuildRequires:  jnr-enxio
BuildRequires:  jnr-ffi >= 0.5.10
BuildRequires:  jnr-netdb
BuildRequires:  jnr-posix >= 1.1.8
BuildRequires:  jnr-unixsocket
BuildRequires:  jzlib
BuildRequires:  joda-time
BuildRequires:  joni >= 1.1.2
BuildRequires:  junit4
BuildRequires:  jzlib
BuildRequires:  nailgun
BuildRequires:  objectweb-asm4
BuildRequires:  snakeyaml
BuildRequires:  yydebug
BuildRequires:  yecht

# these normally get installed as gems during the test process
# TODO: create a condition to be able to test with system gems
# generally, requiring MRI during JRuby build would be nice to avoid
#BuildRequires:  rubygem(rake)
#BuildRequires:  rubygem(rspec-core)
#BuildRequires:  rubygem(rspec-mocks)
#BuildRequires:  rubygem(rspec-expectations)
#BuildRequires:  rubygem(ruby-debug)
#BuildRequires:  rubygem(ruby-debug-base)
#BuildRequires:  rubygem(columnize)

# Java Requires
Requires:  bouncycastle
Requires:  bouncycastle-mail
Requires:  bsf
Requires:  bytelist >= 1.0.8
Requires:  felix-osgi-core >= 1.4.0
Requires:  invokebinder
Requires:  jansi
Requires:  jcodings >= 1.0.1
Requires:  jffi >= 1.0.10
Requires:  jline2 >= 2.7
Requires:  jna
Requires:  jnr-constants
Requires:  jnr-enxio
Requires:  jnr-ffi >= 0.5.10
Requires:  jnr-netdb
Requires:  jnr-posix >= 1.1.8
Requires:  jnr-unixsocket
Requires:  joda-time
Requires:  joni >= 1.1.2
Requires:  jruby-yecht
Requires:  jzlib
Requires:  nailgun
Requires:  objectweb-asm4
Requires:  yydebug

# Other Requires
Requires:  rubygems

Provides:  ruby(abi) = 1.9.1
Provides:  ruby(abi) = 1.8
Provides:  ruby(irb)
Provides:  rubygem(bigdecimal)
Provides:  rubygem(io-console)

%description
JRuby is a 100% Java implementation of the Ruby programming language.
It is Ruby for the JVM. JRuby provides a complete set of core "builtin"
classes and syntax for the Ruby language, as well as most of the Ruby
Standard Libraries.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}

%description    javadoc
Javadoc for %{name}.

# yecht / jruby bindings
# http://jira.codehaus.org/browse/JRUBY-5352
%package        yecht
Summary:        Bindings used to load yecht in jruby
Group:          Development/Libraries
BuildRequires:  yecht
Requires:       yecht
Requires:       %{name} = %{version}-%{release}

%description yecht
The bindings for the yecht library for internal use in jruby

%prep
%setup -q -n %{name}-%{version}%{?preminorver:.%{preminorver}}

%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0
%patch6 -p0

tar xzvf %{SOURCE1}
mv %{yecht_cluster}-yecht-%{yecht_commitversion} yecht

# delete all embedded jars - don't delete test jars!
find -path './test' -prune -o -path './spec' -prune -o -type f -name '*.jar' -exec rm -f '{}' \;

# delete windows specific files
find -name *.exe -exec rm -f '{}' \;
find -name *.dll -exec rm -f '{}' \;

# prebuilt gems seem to do problems with building jruby-yecht bindings => move them someplace else
mkdir build_gems
mv build_lib/*.gem build_gems/
sed -i 's|\.gem=\${build\.lib\.dir}|.gem=build_gems|' default.build.properties

# delete all vcs files
find -name .gitignore -exec rm -f '{}' \;
find -name .cvsignore -exec rm -f '{}' \;

# replace them with symlinks
# these sorted to able to check them against new releases easily
# don't forget to also change these in jruby-add-classpath-to-start-script.patch
build-jar-repository -s -p build_lib \
     objectweb-asm4/asm \
     objectweb-asm4/asm-analysis \
     objectweb-asm4/asm-commons \
     objectweb-asm4/asm-tree \
     objectweb-asm4/asm-util \
     bcprov \
     bcmail \
     bsf \
     bytelist \
     coro-mock \
     invokebinder \
     jansi \
     jarjar \
     jcodings \
     jffi \
     jline2 \
     jna \
     jnr-constants \
     jnr-enxio \
     jnr-ffi \
     jnr-netdb \
     jnr-posix \
     jnr-unixsocket \
     joda-time \
     joni \
     junit \
     junit4 \
     jzlib \
     nailgun \
     felix/org.osgi.core \
     snakeyaml \
     yecht \
     yydebug


# required as jruby was shipping the core java tools jar
ln -s /usr/lib/jvm/java/lib/tools.jar build_lib/apt-mirror-api.jar

# remove hidden .document files
find lib/ruby/ -name '*.document' -exec rm -f '{}' \;

# change included stdlib to use jruby rather than some arcane ruby install
find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/local/bin/ruby|#!/usr/bin/env jruby|" '{}' \;

# lib/ruby scripts shouldn't contain shebangs as they are not executable on their own
find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/local/bin/ruby||" '{}' \;
find lib/ruby/ -name '*.rb' -exec sed --in-place "s|^#!/usr/bin/env ruby||" '{}' \;

# the yecht library needs to be accessible from ruby
pushd yecht
mkdir -p lib/ build/classes/ruby
%patch7 -p0
popd

%build
ant
ant apidocs

# remove bat files
rm bin/*.bat

pushd yecht
ant ext-ruby-jar
popd

%install
install -d -m 755 %{buildroot}%{_datadir}
install -p -d -m 755 %{buildroot}%{_datadir}/%{name}
cp -ar samples/ %{buildroot}%{_datadir}/%{name}/ # samples
cp -ar lib/     %{buildroot}%{_datadir}/%{name}/ # stdlib + jruby.jar
cp -ar bin/     %{buildroot}%{_datadir}/%{name}/ # startup scripts

# /usr prefix startup scripts
install -d -m 755 %{buildroot}%{_bindir}
ln -s %{_datadir}/%{name}/bin/jgem  %{buildroot}%{_bindir}/gem-jruby
ln -s %{_datadir}/%{name}/bin/jirb  %{buildroot}%{_bindir}/irb-jruby
ln -s %{_datadir}/%{name}/bin/jruby %{buildroot}%{_bindir}/jruby

## Fedora integration stuff
# modify the JRuby executable to contain Fedora specific paths redefinitons
# we need to modify jruby{,sh,bash} to be sure everything is ok
sed -i 's|$FEDORA_JAVA_OPTS|-Dvendor.dir.general=%{jruby_vendordir}\
                            -Dsite.dir.general=%{jruby_sitedir}\
                            -Dvendor.dir.rubygems=%{rubygems_dir}|' \
  %{buildroot}%{_datadir}/%{name}/bin/jruby*

# install JRuby specific bits into system RubyGems
mkdir -p %{buildroot}%{rubygems_dir}/rubygems/defaults
cp -a lib/ruby/shared/rubygems/defaults/* %{buildroot}%{rubygems_dir}/rubygems/defaults
pushd %{buildroot}%{rubygems_dir}
patch -p0 < %{PATCH9}
popd


# javadoc
install -p -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -a docs/api/* %{buildroot}%{_javadocdir}/%{name}

# jruby-yecht
install -d -m 755 %{buildroot}%{_javadir}
cp yecht/lib/yecht-ruby-0.0.2.jar %{buildroot}%{_datadir}/%{name}-yecht.jar
ln -s %{_datadir}/%{name}-yecht.jar %{buildroot}%{_javadir}/%{name}-yecht.jar

# pom
%add_to_maven_depmap org.jruby %{name} %{version} JPP %{name}
mkdir -p $RPM_BUILD_ROOT%{_mavenpomdir}
cp -a pom.xml $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-java.pom

# java dir
install -d -m 755 %{buildroot}%{_javadir}
ln -s %{_datadir}/%{name}/lib/%{name}.jar %{buildroot}%{_javadir}/%{name}.jar

%check
%if 0%{?enable_check}
cp yecht/lib/yecht-ruby-0.0.2.jar build_lib/%{name}-yecht.jar
cp lib/%{name}.jar build_lib/%{name}.jar
# explicitly set path to jruby.jar and jruby-yecht.jar, as they can't found by "build-classpath" used in bin/jruby
export JRUBY_CP=$(pwd)/build_lib/jruby.jar:$(pwd)/build_lib/jruby-yecht.jar

export LANG=en_US.utf8
ant test
%endif

%files
%doc COPYING
%doc docs/CodeConventions.txt docs/README.test

%{_bindir}/%{name}
%{_bindir}/gem-jruby
%{_bindir}/irb-jruby
%{_datadir}/%{name}
# exclude bundled gems
%exclude %{jruby_vendordir}/ruby/1.9/json*
%exclude %{jruby_vendordir}/ruby/1.9/rdoc*
%exclude %{jruby_vendordir}/ruby/1.9/rake*
# exclude all of the rubygems stuff
%exclude %{jruby_vendordir}/ruby/shared/*ubygems*
%exclude %{jruby_vendordir}/ruby/shared/rbconfig
# own the JRuby specific files under RubyGems dir
%{rubygems_dir}/rubygems/defaults/jruby.rb
%{_javadir}/%{name}.jar

%{_mavendepmapfragdir}/%{name}
%{_mavenpomdir}/*

%files javadoc
%{_javadocdir}/%{name}

%files yecht
%{_datadir}/%{name}-yecht.jar
%{_javadir}/%{name}-yecht.jar

%changelog
* Tue Oct 23 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-1
- Updated to JRuby 1.7.0.

* Thu Oct 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.3.RC2
- Updated to JRuby 1.7.0.RC2.
- Rename jirb and jgem to irb-jruby and gem-jruby.

* Thu Oct 04 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.2.RC1
- Use system RubyGems.
- Add path definition that brings JRuby closer to MRI.

* Mon Oct 01 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.1.RC1
- Updated to JRuby 1.7.0.RC1.

* Tue Sep 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.7.0-0.1.preview2
- Updated to JRuby 1.7.0.preview2.

* Thu May 17 2012 Vít Ondruch <vondruch@redhat.com> - 1.6.7.2-1
- Updated to JRuby 1.6.7.2.

* Fri Jan 13 2012 Mo Morsi <mmorsi@redhat.com> - 1.6.3-3
- rename jaffl dependency to jnr-ffi (BZ#723191)
- change build dep on rspec 1.x to 2.x

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.3-1
- update to latest upstream release
- include missing symlink to jruby-yecht

* Wed Jul 06 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.2-2
- install jruby to _datadir not _javadir
- remove windows specific files (exes, dlls, etc)

* Wed May 25 2011 Mo Morsi <mmorsi@redhat.com> - 1.6.2-1
- Updated to latest upstream release

* Tue Dec 07 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.6-2
- Remove pre-built gems
- Started to add bits to get test suite in working order
- Added yecht bindings used internally in jruby

* Mon Dec 06 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.6-1
- Updated jruby to latest upstream release
- Updates to conform to pkging guidelines

* Thu Dec 02 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.5-1
- Updated jruby to latest upstream release

* Mon Oct 25 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.5.3-1
- Updated jruby to latest upstream release

* Thu Jan 28 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.4.0-1
- Unorphaned / updated jruby

* Fri Mar 6 2009 Conrad Meyer <konrad@tylerc.org> - 1.1.6-3
- debug_package nil, as this is a pure-java package (that can't
  be built with gcj).

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 18 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.6-1
- Bump to 1.1.6.

* Fri Nov 28 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.5-1
- Bump to 1.1.5.

* Mon Sep 8 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.4-1
- Bump to 1.1.4.

* Tue Jul 29 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.3-2
- Update jruby-fix-jruby-start-script.patch to work with faster
  class-loading mechanism introduced in JRuby 1.1.2.

* Sat Jul 19 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.3-1
- Bump to 1.1.3.

* Wed May 21 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-7
- Require joni and jline.

* Thu Apr 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-6
- Bump because F-9 bumped.

* Thu Apr 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-5
- BR and Requires openjdk.

* Tue Apr 22 2008 Conrad Meyer <konrad@tylerc.org> - 1.1.1-4
- Add check section.
- Removed patches 0 and 4 because they got incorporated in upstream.

* Mon Apr 7 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-3
- Install all jruby to the prefix libdir/jruby, linking from /usr
  where needed.

* Sun Apr 6 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-2
- Add a few missing Requires.
- Add some things that were missing from CP in the start script.

* Sun Mar 30 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-1
- Bump to 1.1.
- Remove binary .jars.
- Minor cleanups in the specfile.
- Don't include jruby stdlib (for now).

* Sun Feb 24 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-0.4.20080216svn
- Bump for 1.1rc2.

* Tue Jan 8 2008 Conrad Meyer <konrad@tylerc.org> - 1.1-0.3.20080108svn
- Bump for 1.1rc1.

* Sun Dec 9 2007 Conrad Meyer <konrad@tylerc.org> - 1.1-0.2.20071209svn
- SVN version bump.

* Mon Dec 3 2007 Conrad Meyer <konrad@tylerc.org> - 1.1-0.1.20071203svn
- Initial package created from ancient jpackage package
