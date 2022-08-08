import { AtSignIcon } from "@chakra-ui/icons";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Icon,
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { PageMeta } from "../../casualcms/domain/model";

type PageBreadcrumbProps = {
  meta: PageMeta;
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
  const meta = props.meta;
  return (
    <Breadcrumb>
      <BreadcrumbItem>
        <Link to="/admin/pages">
          <Icon as={HomeIcon} />
        </Link>
      </BreadcrumbItem>
      {meta.breadcrumb.map((item, i) => (
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
      {props.title && (
        <BreadcrumbItem>
          <BreadcrumbLink href="#">{props.title}</BreadcrumbLink>
        </BreadcrumbItem>
      )}
    </Breadcrumb>
  );
};
