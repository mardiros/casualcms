import { Breadcrumb, BreadcrumbItem, Icon } from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { Draft, Setting, Site, Snippet } from "../../casualcms/domain/model";

type PageBreadcrumbProps = {
  page?: Draft | null;
  title?: string;
};

type SiteBreadcrumbProps = {
  site?: Site | null;
  title?: string;
};

type SnippetBreadcrumbProps = {
  snippet?: Snippet | null;
  title?: string;
};

type SettingBreadcrumbProps = {
  hostname?: string;
  title?: string;
};

export const HomeIcon = (): JSX.Element => {
  return (
    <svg viewBox="0 0 16 16" width="1em">
      <path
        fill="currentColor"
        d="M14 16c.6 0 1-.4 1-1V6c0-.3-.1-.6-.4-.8l-6-5c-.4-.3-.9-.3-1.3
        0l-6 5c-.2.2-.3.5-.3.8v9c0 .6.4 1 1 1h4v-5h4v5h4z"
      />
    </svg>
  );
};

export const PageBreadcrumb: React.FunctionComponent<PageBreadcrumbProps> = (
  props: PageBreadcrumbProps
) => {
  const { page, title } = props;
  return (
    <Breadcrumb padding={5}>
      <BreadcrumbItem>
        <Link to="/admin/pages">
          <Icon as={HomeIcon} />
        </Link>
      </BreadcrumbItem>
      {page &&
        page.meta.breadcrumb.map((item, i) => (
          <BreadcrumbItem key={i}>
            <Link
              to={`/admin/pages/?${new URLSearchParams({
                parent: item.path,
              })}`}
              title={item.title}
            >
              {item.slug}
            </Link>
          </BreadcrumbItem>
        ))}
      {title && (
        <BreadcrumbItem>
          <span>{title}</span>
        </BreadcrumbItem>
      )}
    </Breadcrumb>
  );
};

export const SiteBreadcrumb: React.FunctionComponent<SiteBreadcrumbProps> = (
  props: SiteBreadcrumbProps
) => {
  const { site, title } = props;
  return (
    <Breadcrumb padding={5}>
      <BreadcrumbItem>
        <Link to="/admin/sites">
          <Icon as={HomeIcon} />
        </Link>
      </BreadcrumbItem>
      {site && (
        <BreadcrumbItem>
          <Link to={`/admin/sites/edit?hostname=${site.hostname}`}>
            {site.hostname}
          </Link>
        </BreadcrumbItem>
      )}
      {title && (
        <BreadcrumbItem>
          <span>{title}</span>
        </BreadcrumbItem>
      )}
    </Breadcrumb>
  );
};

export const SnippetBreadcrumb: React.FunctionComponent<
  SnippetBreadcrumbProps
> = (props: SnippetBreadcrumbProps) => {
  const { snippet, title } = props;
  return (
    <Breadcrumb padding={5}>
      <BreadcrumbItem>
        <Link to="/admin/snippets">
          <Icon as={HomeIcon} />
        </Link>
      </BreadcrumbItem>
      {snippet && (
        <BreadcrumbItem>
          <Link
            to={`/admin/snippets/edit/${snippet.meta.type}/${snippet.key}`}
          >
            {snippet.key}
          </Link>
        </BreadcrumbItem>
      )}
      {title && (
        <BreadcrumbItem>
          <span>{title}</span>
        </BreadcrumbItem>
      )}
    </Breadcrumb>
  );
};

export const SettingBreadcrumb: React.FunctionComponent<
  SettingBreadcrumbProps
> = (props: SettingBreadcrumbProps) => {
  const { hostname, title } = props;
  return (
    <Breadcrumb padding={5}>
      <BreadcrumbItem>
        <Link to="/admin/settings">
          <Icon as={HomeIcon} />
        </Link>
      </BreadcrumbItem>
      {hostname && (
        <BreadcrumbItem>
          <Link to={`/admin/settings/${hostname}`}>{hostname}</Link>
        </BreadcrumbItem>
      )}
      {title && (
        <BreadcrumbItem>
          <span>{title}</span>
        </BreadcrumbItem>
      )}
    </Breadcrumb>
  );
};
