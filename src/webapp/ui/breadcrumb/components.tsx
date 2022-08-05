import {
  Breadcrumb,
  BreadcrumbItem,
} from "@chakra-ui/react";
import { Link } from "react-router-dom";
import { PageMeta } from "../../casualcms/domain/model";

type PageBreadcrumbProps = {
  meta: PageMeta;
};

export const PageBreadcrumb: React.FunctionComponent<PageBreadcrumbProps> = (props: PageBreadcrumbProps) => {
  const meta = props.meta;
  return (
    <Breadcrumb>
      {meta.breadcrumb.map((item, i) => (
        <BreadcrumbItem key={i}>
          <Link to={`/admin/pages/?${new URLSearchParams({
            parent: item.path,
          })}`} title={item.title}>
            {item.slug}
          </Link>
        </BreadcrumbItem>
      ))}
    </Breadcrumb>
  );
};
